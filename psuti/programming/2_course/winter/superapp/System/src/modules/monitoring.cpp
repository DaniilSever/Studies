#include "monitoring.h"
#include "settings.h"
#include <QtWidgets>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QHostInfo>
#include <QDateTime>
#include <QFileInfo>
#include <QDir>
#include <QFileDialog>
#include <pwd.h>
#include <unistd.h>
#include <sys/stat.h>
#include <algorithm>
namespace {
QByteArray readBinary(QString path){QFile f(path);return f.open(QIODevice::ReadOnly)?f.readAll():QByteArray();}
QString read(QString path){return QString::fromUtf8(readBinary(path));}
QString timestamp(){return QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss");}
QString startTime(qulonglong t){double up=read("/proc/uptime").section(' ',0,0).toDouble();double boot=QDateTime::currentSecsSinceEpoch()-up;return t?QDateTime::fromSecsSinceEpoch(qint64(boot+t/double(sysconf(_SC_CLK_TCK)))).toString("HH:mm:ss"):"?";}
QString uidName(int uid){if(uid<0)return "-";auto *p=getpwuid(uid);return p?QString::fromLocal8Bit(p->pw_name):QString::number(uid);}
}
monitoring_ui::monitoring_ui(QWidget*p):QMainWindow(p){setWindowTitle(cfg::MONITORING_TITLE);resize(cfg::MONITORING_SIZE);
 auto add=[this](QString id,QString title,QString shortcut){auto*a=new QAction(title,this);if(!shortcut.isEmpty())a->setShortcut(QKeySequence(shortcut));actions[id]=a;return a;};
 auto*m=menuBar()->addMenu("Мониторинг");for(auto e:QList<QStringList>{{"start","Запустить мониторинг","Ctrl+M"},{"stop","Остановить мониторинг","Ctrl+T"},{"refresh","Обновить","F5"},{"save_report","Сохранить отчёт...","Ctrl+S"},{"hostname","Имя компьютера","Ctrl+G"},{"log","Сохранить журнал ФМ...","Ctrl+Shift+L"},{"hostname_log","Сохранить лог компьютера...",""},{"exit","Закрыть","Ctrl+W"}})m->addAction(add(e[0],e[1],e[2]));
 auto*help=menuBar()->addMenu("Справка");help->addAction(add("about","О мониторинге","F1"));
 auto*c=new QWidget;auto*l=new QVBoxLayout(c);l->setContentsMargins(8,8,8,8);auto*bar=new QHBoxLayout;
 for(auto e:QList<QPair<QString,QString>>{{"start","Запустить"},{"stop","Остановить"},{"refresh","Обновить"},{"save_report","Сохранить отчёт"},{"hostname","Имя компьютера"},{"log","Журнал ФМ"}}){auto*b=new QPushButton(e.second);connect(b,&QPushButton::clicked,actions[e.first],&QAction::trigger);bar->addWidget(b);}bar->addStretch();l->addLayout(bar);
 table=new QTableWidget(0,5);table->setHorizontalHeaderLabels({"PID","Имя","Пользователь","Время старта","Состояние"});table->setEditTriggers(QAbstractItemView::NoEditTriggers);table->setSelectionBehavior(QAbstractItemView::SelectRows);table->setAlternatingRowColors(true);
 table->horizontalHeader()->setSectionResizeMode(0,QHeaderView::ResizeToContents);table->horizontalHeader()->setSectionResizeMode(1,QHeaderView::Stretch);for(int i=2;i<5;i++)table->horizontalHeader()->setSectionResizeMode(i,QHeaderView::ResizeToContents);l->addWidget(table);
 status=new QLabel("Мониторинг остановлен");l->addWidget(status);setCentralWidget(c);
}
void monitoring_ui::setRunning(bool b){actions["start"]->setEnabled(!b);actions["stop"]->setEnabled(b);}
monitoring_func::monitoring_func(QWidget*p):monitoring_ui(p){refreshTimer.setInterval(cfg::MONITORING_REFRESH_MS);popupTimer.setInterval(cfg::MONITORING_REFRESH_MS);
 connect(&refreshTimer,&QTimer::timeout,this,&monitoring_func::refresh);connect(&popupTimer,&QTimer::timeout,this,&monitoring_func::hostnamePush);
 auto wire=[this](QString id,auto f){connect(actions[id],&QAction::triggered,this,f);};
 wire("start",[this]{start();});wire("stop",[this]{stop();});wire("refresh",[this]{refresh();});wire("save_report",[this]{saveReport();});wire("hostname",[this]{hostnamePopup();});wire("log",[this]{saveJournal();});wire("hostname_log",[this]{saveHostnameLog();});wire("exit",[this]{close();});wire("about",[this]{QMessageBox::about(this,"О мониторинге",QString(cfg::ABOUT_TEXT_MONITORING).replace("Python + PyQt5","C++ + Qt"));});setRunning(false);}
monitoring_func::~monitoring_func(){hostnameStop();}
QSet<qint64> monitoring_func::pids()const{QSet<qint64> ret;QDir d("/proc");for(QString n:d.entryList(QDir::Dirs|QDir::NoDotAndDotDot)){bool ok=false;qint64 pid=n.toLongLong(&ok);if(ok)ret.insert(pid);}return ret;}
bool monitoring_func::isApp(qint64 pid)const{if(appPids.contains(pid))return true;QByteArray cmd=readBinary(QString("/proc/%1/cmdline").arg(pid));for(auto s:{"superapp_terminal","superapp_popup","superapp_monitoring","superapp ","filemanager.py","terminal.py","monitoring.py","popup.py","app.py","main.py"})if(cmd.contains(s))return true;return false;}
ProcessInfo monitoring_func::processInfo(qint64 pid)const{ProcessInfo p;p.pid=pid;QString stat=read(QString("/proc/%1/stat").arg(pid));int open=stat.indexOf('('),close=stat.lastIndexOf(')');if(open<0||close<=open)return {};p.name=stat.mid(open+1,close-open-1);
 auto rest=stat.mid(close+2).split(' ',Qt::SkipEmptyParts);if(rest.size()<20)return {};p.state=rest[0];p.ticks=rest[19].toULongLong();
 QByteArray cmd=readBinary(QString("/proc/%1/cmdline").arg(pid));if(!cmd.isEmpty()){QString exe=QString::fromLocal8Bit(cmd.split('\0').first());if(!exe.isEmpty())p.name=QFileInfo(exe).fileName();}
 int uid=-1;for(auto line:read(QString("/proc/%1/status").arg(pid)).split('\n'))if(line.startsWith("Uid:")){auto parts=line.simplified().split(' ');if(parts.size()>1)uid=parts[1].toInt();break;}
 p.user=uidName(uid);p.start=startTime(p.ticks);return p;}
void monitoring_func::start(){baseline=pids();started.clear();refresh();refreshTimer.start();setRunning(true);status->setText(QString("Мониторинг запущен. Обновление каждые %1 мс.").arg(cfg::MONITORING_REFRESH_MS));}
void monitoring_func::stop(){refreshTimer.stop();setRunning(false);status->setText("Мониторинг остановлен");}
void monitoring_func::refresh(){auto ids=pids().values();std::sort(ids.begin(),ids.end());table->setRowCount(0);int n=0;for(auto id:ids){if(isApp(id))continue;auto p=processInfo(id);if(!p.pid)continue;int row=table->rowCount();table->insertRow(row);QStringList cols={QString::number(p.pid),p.name,p.user,p.start,p.state};for(int i=0;i<cols.size();++i){auto*item=new QTableWidgetItem(cols[i]);if(i==0)item->setTextAlignment(Qt::AlignRight|Qt::AlignVCenter);table->setItem(row,i,item);}n++;if(!baseline.contains(id))started[id]=qMakePair(p.name,p.start);}
 status->setText(QString("Процессов: %1  |  новых за сессию: %2  |  обновлено: %3").arg(n).arg(started.size()).arg(QTime::currentTime().toString("HH:mm:ss")));}
void monitoring_func::saveReport(){if(started.isEmpty()){QMessageBox::information(this,"Отчёт",cfg::MSG_NO_REPORT);return;}QString path=QFileDialog::getSaveFileName(this,"Сохранить отчёт",cfg::appRoot()+"/report_"+QDateTime::currentDateTime().toString("yyyyMMdd_HHmmss")+".txt","Текстовые файлы (*.txt);;Все файлы (*)");if(path.isEmpty())return;
 QFile f(path);if(!f.open(QIODevice::WriteOnly|QIODevice::Text)){QMessageBox::critical(this,"Отчёт","Не удалось сохранить отчёт: "+f.errorString());return;}QString header=cfg::REPORT_HEADER;header.replace("{ts}",timestamp()).replace("{n}",QString::number(started.size()));f.write(header.toUtf8());for(auto pair:started){f.write((pair.first.leftJustified(30,' ')+"  "+pair.second+"\n").toUtf8());}QMessageBox::information(this,"Отчёт",QString("Отчёт сохранён:\n%1\nПроцессов: %2").arg(path).arg(started.size()));}
QList<QPair<QString,QString>> monitoring_func::hostnameFields()const{QList<QPair<QString,QString>> a;QString name=QHostInfo::localHostName();if(!name.isEmpty())a<<qMakePair(QString("Имя компьютера"),name);QString fqdn=QHostInfo::localDomainName();if(!fqdn.isEmpty()&&fqdn!=name)a<<qMakePair(QString("FQDN"),name+"."+fqdn);
 QString proc=read("/proc/sys/kernel/hostname").trimmed();if(!proc.isEmpty()&&proc!=name)a<<qMakePair(QString("Имя (ядро, /proc)"),proc);QString etc=read("/etc/hostname").trimmed();if(!etc.isEmpty()&&etc!=name)a<<qMakePair(QString("Имя (/etc/hostname)"),etc);
 for(auto l:read("/etc/resolv.conf").split('\n'))if(l.startsWith("domain ")){a<<qMakePair(QString("Домен"),l.section(' ',1).trimmed());break;}a<<qMakePair(QString("Обновлено"),QTime::currentTime().toString("HH:mm:ss"));return a;}
void monitoring_func::hostnamePopup(){if(popupProcess&&popupProcess->state()!=QProcess::NotRunning){QMessageBox::information(this,"Имя компьютера","Окно информации уже открыто.");return;}
 hostnameStop();server=new QTcpServer(this);if(!server->listen(QHostAddress::LocalHost,0)){QMessageBox::critical(this,"Имя компьютера",cfg::MSG_POPUP_FAIL+server->errorString());hostnameStop();return;}
 connect(server,&QTcpServer::newConnection,this,[this]{if(client)return;client=server->nextPendingConnection();connect(client,&QTcpSocket::readyRead,this,[this]{QByteArray d=client->readAll();if(d.contains("\"bye\"")||d.contains("\"close\""))hostnameStop();});connect(client,&QTcpSocket::disconnected,this,&monitoring_func::hostnameStop);hostnamePush();});
 popupProcess=new QProcess(this);connect(popupProcess,QOverload<int,QProcess::ExitStatus>::of(&QProcess::finished),this,[this](int,QProcess::ExitStatus){hostnameStop();});popupProcess->start(cfg::siblingExecutable("popup"),{cfg::POPUP_HOST,QString::number(server->serverPort())});if(!popupProcess->waitForStarted(1000)){QMessageBox::critical(this,"Имя компьютера","Не удалось запустить popup");hostnameStop();return;}appPids.insert(popupProcess->processId());popupTimer.start();status->setText(QString("Окно «Имя компьютера» открыто (сокет %1:%2). Обновление в реальном времени.").arg(cfg::POPUP_HOST).arg(server->serverPort()));}
void monitoring_func::hostnamePush(){if(!client||client->state()!=QTcpSocket::ConnectedState)return;QJsonArray fields;for(auto e:hostnameFields()){QJsonObject obj;obj["label"]=e.first;obj["value"]=e.second;fields.append(obj);}QJsonObject data;data["type"]="data";data["title"]="Имя компьютера (вар. 1)";data["fields"]=fields;client->write(QJsonDocument(data).toJson(QJsonDocument::Compact)+"\n");}
void monitoring_func::hostnameStop(){popupTimer.stop();if(client){auto*c=client;client=nullptr;if(c->state()==QTcpSocket::ConnectedState){c->write("{\"type\":\"close\"}\n");c->flush();}c->disconnect(this);c->disconnectFromHost();c->deleteLater();}if(server){server->close();server->deleteLater();server=nullptr;}if(popupProcess){auto*p=popupProcess;popupProcess=nullptr;appPids.remove(p->processId());p->disconnect(this);if(p->state()!=QProcess::NotRunning)p->terminate();p->deleteLater();}}
void monitoring_func::saveJournal(){
 QString dest=QFileDialog::getSaveFileName(this,"Сохранить журнал файлового менеджера",cfg::appRoot()+"/fm_journal_"+QDateTime::currentDateTime().toString("yyyyMMdd_HHmmss")+".txt","Текстовые файлы (*.txt);;Все файлы (*)");if(dest.isEmpty())return;
 QFile src(cfg::journalPath());if(!src.open(QIODevice::ReadOnly|QIODevice::Text)){QMessageBox::information(this,"Журнал ФМ","Журнал пуст: файловый менеджер ещё не запускался или событий не было.");return;}
 QStringList entries;for(auto e:QString::fromUtf8(src.readAll()).split('\n'))if(!e.trimmed().isEmpty())entries<<e;
 int visits=0;for(auto e:entries)if(e.contains("переход в каталог"))visits++;
 QFile dst(dest);if(!dst.open(QIODevice::WriteOnly|QIODevice::Text)){QMessageBox::critical(this,"Журнал ФМ","Не удалось сохранить журнал: "+dst.errorString());return;}
 QString data="Журнал «Супрапп» — посещения и операции файлового менеджера\n";
 data+="Сохранён: "+timestamp()+"\n"+QString("Всего событий: %1, посещений каталогов: %2\n").arg(entries.size()).arg(visits)+"----------------------------------------\n"+entries.join("\n")+"\n";
 dst.write(data.toUtf8());QMessageBox::information(this,"Журнал ФМ",QString("Журнал файлового менеджера сохранён:\n%1\nЗаписей: %2").arg(dest).arg(entries.size()));
}
void monitoring_func::saveHostnameLog(){
 QString dest=QFileDialog::getSaveFileName(this,"Сохранить лог (имя компьютера)",cfg::appRoot()+"/hostname_log_"+QDateTime::currentDateTime().toString("yyyyMMdd_HHmmss")+".txt","Текстовые файлы (*.txt);;Все файлы (*)");if(dest.isEmpty())return;
 QFile f(dest);if(!f.open(QIODevice::WriteOnly|QIODevice::Text)){QMessageBox::critical(this,"Лог-файл","Не удалось сохранить лог: "+f.errorString());return;}
 QString data="Лог «Суперапп» — информация о компьютере (имя хоста)\nВремя: "+timestamp()+"\n----------------------------------------\n";
 auto fields=hostnameFields();if(fields.isEmpty())data+=cfg::MSG_HOSTNAME_UNAVAIL+"\n";else for(auto e:fields)data+=e.first+": "+e.second+"\n";
 f.write(data.toUtf8());QMessageBox::information(this,"Лог-файл","Лог-файл сохранён:\n"+dest);
}
