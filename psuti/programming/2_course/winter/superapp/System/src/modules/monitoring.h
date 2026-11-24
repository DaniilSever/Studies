#pragma once
#include <QMainWindow>
#include <QTimer>
#include <QTableWidget>
#include <QTcpServer>
#include <QTcpSocket>
#include <QProcess>
#include <QSet>
#include <QMap>
#include <QLabel>
struct ProcessInfo{qint64 pid=0;QString name,user,start,state;qulonglong ticks=0;};
class monitoring_ui:public QMainWindow{
 Q_OBJECT
public:
 explicit monitoring_ui(QWidget*parent=nullptr);
protected:
 QTableWidget*table;QLabel*status;QMap<QString,QAction*>actions;
 void setRunning(bool running);
};
class monitoring_func:public monitoring_ui{
 Q_OBJECT
public:
 explicit monitoring_func(QWidget*parent=nullptr);
 ~monitoring_func() override;
private:
 QTimer refreshTimer,popupTimer;
 QSet<qint64> baseline,appPids;
 QMap<qint64,QPair<QString,QString>> started;
 QTcpServer*server=nullptr;QTcpSocket*client=nullptr;QProcess*popupProcess=nullptr;
 QSet<qint64> pids()const;bool isApp(qint64 pid)const;ProcessInfo processInfo(qint64 pid)const;
 void start();void stop();void refresh();void saveReport();void saveJournal();void saveHostnameLog();
 void hostnamePopup();void hostnamePush();void hostnameStop();
 QList<QPair<QString,QString>> hostnameFields()const;
};
