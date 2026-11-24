#include "filemanager.h"
#include "settings.h"
#include <QtWidgets>
#include <QDesktopServices>
#include <QDateTime>
#include <QMimeData>
#include <QUrl>
#include <QProcess>
#include <QFileInfo>
#include <QDirIterator>
#include <algorithm>
#include <functional>
namespace {
QString stamp(){return QTime::currentTime().toString("HHmmss");}
QString normal(QString p){return QDir::cleanPath(QFileInfo(p).absoluteFilePath());}
bool isProtected(QString path){return QFileInfo(path).fileName()==cfg::SYSTEM_FOLDER;}
bool copyTree(const QString &src,const QString &dst){
 QFileInfo fi(src); if(fi.isSymLink()) return QFile::link(fi.symLinkTarget(),dst);
 if(fi.isFile())return QFile::copy(src,dst);
 if(!fi.isDir() || !QDir().mkpath(dst))return false;
 QDir d(src);
 for(const QFileInfo &e:d.entryInfoList(QDir::AllEntries|QDir::NoDotAndDotDot|QDir::Hidden|QDir::System))
   if(!copyTree(e.absoluteFilePath(),dst+"/"+e.fileName()))return false;
 QFile::setPermissions(dst,fi.permissions()); return true;
}
bool removeTree(const QString &p){return QFileInfo(p).isDir()&&!QFileInfo(p).isSymLink()?QDir(p).removeRecursively():QFile::remove(p);}
bool moveTree(QString a,QString b){if(QDir().rename(a,b))return true; if(!copyTree(a,b))return false;return removeTree(a);}
QString uniqueDst(QString dst){if(QFileInfo::exists(dst)) dst+=" ("+stamp()+")";return dst;}
QString humanSize(qint64 n){double v=n;QStringList units={"Б","КБ","МБ","ГБ","ТБ"};int i=0;while(v>=1024&&i<4){v/=1024;i++;}return QString::number(v,'f',i?1:0)+" "+units[i];}
}
FolderListWidget::FolderListWidget(QWidget*p):QListWidget(p){
 setDragEnabled(true);
 setAcceptDrops(true);
 viewport()->setAcceptDrops(true);
 setDropIndicatorShown(true);
 setDragDropMode(QAbstractItemView::DragDrop);
 setDefaultDropAction(Qt::MoveAction);
}
void FolderListWidget::setMovement(QListView::Movement movement){
 // QListView::setMovement(Static) resets some drag/drop state internally.
 // Restore the configuration just as in the original PyQt5 FolderListWidget.
 QListWidget::setMovement(movement);
 setDragEnabled(true);
 setAcceptDrops(true);
 viewport()->setAcceptDrops(true);
 setDropIndicatorShown(true);
 setDragDropMode(QAbstractItemView::DragDrop);
 setDefaultDropAction(Qt::MoveAction);
}
QMimeData *FolderListWidget::mimeData(const QList<QListWidgetItem*>& items)const{
 auto *m=QListWidget::mimeData(items);if(!m)m=new QMimeData;
 QList<QUrl> urls;for(auto*i:items)urls.append(QUrl::fromLocalFile(i->data(cfg::FILEMANAGER_ROLE_PATH).toString()));m->setUrls(urls);return m;
}
void FolderListWidget::dragEnterEvent(QDragEnterEvent*e){if(e->mimeData()->hasUrls()||e->source()==this)e->acceptProposedAction();else e->ignore();}
void FolderListWidget::dragMoveEvent(QDragMoveEvent*e){if(e->mimeData()->hasUrls()||e->source()==this)e->acceptProposedAction();else e->ignore();}
void FolderListWidget::dropEvent(QDropEvent*e){
 bool internal=e->source()==this||e->mimeData()->hasFormat("application/x-qabstractitemmodeldatalist");QStringList paths;
 for(auto u:e->mimeData()->urls())if(u.isLocalFile())paths<<u.toLocalFile();
 if(internal&&paths.isEmpty())for(auto*i:selectedItems())paths<<i->data(cfg::FILEMANAGER_ROLE_PATH).toString();
#if QT_VERSION >= QT_VERSION_CHECK(6,0,0)
 auto*it=itemAt(e->position().toPoint());
#else
 auto*it=itemAt(e->pos());
#endif
 QString target=it&&it->data(cfg::FILEMANAGER_ROLE_KIND)=="dir"?it->data(cfg::FILEMANAGER_ROLE_PATH).toString():currentDir;
 if(paths.isEmpty()||target.isEmpty()){e->ignore();return;}e->setDropAction(internal?Qt::MoveAction:Qt::CopyAction);e->accept();emit pathsDropped(paths,target,internal);
}
filemanager_ui::filemanager_ui(QWidget*p):QMainWindow(p){
 setWindowTitle(cfg::FILEMANAGER_TITLE);resize(cfg::FILEMANAGER_SIZE);
 folderIcon=QIcon(cfg::assetsDir()+"/folder-icon.png");fileIcon=QIcon(cfg::assetsDir()+"/file-icon.png");
 auto add=[&](QString id,QString label,QString shortcut="",QIcon icon={}){
 auto *a=new QAction(icon,label,this);if(!shortcut.isEmpty())a->setShortcut(QKeySequence(shortcut));actions[id]=a;return a;};
 auto *st=style();
 add("new_folder","Создать папку","Ctrl+Shift+N",st->standardIcon(QStyle::SP_DirIcon));add("new_file","Создать файл","Ctrl+Shift+F",st->standardIcon(QStyle::SP_FileIcon));
 add("search","Поиск файлов и папок...","Ctrl+F");add("open_terminal","Открыть терминал","F4");add("open_monitoring","Мониторинг процессов","Ctrl+M");add("exit","Выход","Ctrl+Q");
 add("cut","Вырезать","Ctrl+X");add("copy","Копировать","Ctrl+C");add("paste","Вставить","Ctrl+V");add("select_all","Выделить всё","Ctrl+A");
 add("open","Открыть","Return");add("open_in_popup","Открыть в новом окне");add("rename","Переименовать","F2");
 add("delete_trash","Удалить в корзину","Delete");add("delete_perm","Удалить безвозвратно","Shift+Delete");add("properties","Свойства","Alt+Return");
 add("refresh","Обновить","F5",st->standardIcon(QStyle::SP_BrowserReload));add("toggle_hidden","Показывать скрытые","Ctrl+H")->setCheckable(true);
 add("back","Назад","Alt+Left",st->standardIcon(QStyle::SP_ArrowLeft));add("forward","Вперёд","Alt+Right",st->standardIcon(QStyle::SP_ArrowRight));add("up","Вверх","Alt+Up",st->standardIcon(QStyle::SP_ArrowUp));
 add("removable","Съёмные носители...","",st->standardIcon(QStyle::SP_DriveHDIcon));add("hotkeys","Горячие клавиши","F1");add("about","О программе");
 auto menu=[&](QString name,QStringList ids){auto*m=menuBar()->addMenu(name);for(auto id:ids){if(id.isEmpty())m->addSeparator();else m->addAction(actions[id]);}};
 menu("Файл",{"new_folder","new_file","","search","","open_terminal","open_monitoring","","exit"});
 menu("Правка",{"cut","copy","paste","","rename","delete_trash","delete_perm","","select_all"});menu("Вид",{"refresh","toggle_hidden"});
 menu("Переход",{"back","forward","up","","removable"});menu("Терминал",{"open_terminal"});menu("Мониторинг",{"open_monitoring"});menu("Справка",{"hotkeys","","about"});
 auto*tb=addToolBar("Навигация");tb->setMovable(false);tb->setIconSize({16,16});for(QString id:{"back","forward","up","refresh"})tb->addAction(actions[id]);tb->addSeparator();
 pathBar=new QLineEdit;pathBar->setPlaceholderText("Путь...");pathBar->setToolTip("Текущий путь. Enter — перейти.");tb->addWidget(pathBar);
 auto*c=new QWidget;auto*lay=new QVBoxLayout(c);lay->setContentsMargins(0,0,0,0);lay->setSpacing(0);
 list=new FolderListWidget;list->setViewMode(QListWidget::IconMode);list->setIconSize(cfg::FILEMANAGER_ICON_SIZE);list->setGridSize(cfg::FILEMANAGER_GRID_SIZE);
 list->setResizeMode(QListWidget::Adjust);list->setMovement(QListWidget::Static);list->setUniformItemSizes(true);list->setSpacing(8);list->setFrameShape(QFrame::NoFrame);
 // Qt resets drag-drop mode when movement is changed.
 list->setDragEnabled(true);list->setAcceptDrops(true);list->viewport()->setAcceptDrops(true);list->setDropIndicatorShown(true);list->setDragDropMode(QAbstractItemView::DragDrop);list->setDefaultDropAction(Qt::MoveAction);
 lay->addWidget(list);setCentralWidget(c);
}
void filemanager_ui::contextMenuEvent(QContextMenuEvent*e){
 auto*it=list->itemAt(list->viewport()->mapFromGlobal(e->globalPos()));QMenu m(this);
 if(it){for(QString id:{"open","open_in_popup"})m.addAction(actions[id]);m.addSeparator();for(QString id:{"rename","delete_trash","delete_perm"})m.addAction(actions[id]);m.addSeparator();m.addAction(actions["properties"]);m.addSeparator();}
 m.addAction(actions["new_folder"]);m.addAction(actions["new_file"]);m.exec(e->globalPos());
}
filemanager_func::filemanager_func(QWidget*p):filemanager_ui(p){
 journal("start","запуск файлового менеджера");auto wire=[&](QString id,std::function<void()>f){connect(actions[id],&QAction::triggered,this,[f](bool){f();});};
 wire("back",[this]{if(historyPos>0)navigate(history[--historyPos],false);});wire("forward",[this]{if(historyPos+1<history.size())navigate(history[++historyPos],false);});
 wire("up",[this]{auto c=currentDir();if(!topLevelRoot(c))navigate(QFileInfo(c).dir().absolutePath());});
 wire("refresh",[this]{reload();});connect(pathBar,&QLineEdit::returnPressed,this,[this]{if(!navigate(pathBar->text().trimmed()))pathBar->setText(currentDir());});
 connect(list,&QListWidget::itemDoubleClicked,this,[this](QListWidgetItem*i){openItem(i);});
 connect(list,&FolderListWidget::pathsDropped,this,&filemanager_func::dropped);
 wire("new_folder",[this]{createEntry(true);});wire("new_file",[this]{createEntry(false);});wire("search",[this]{search();});
 wire("open",[this]{openItem(selected());});wire("open_in_popup",[this]{openItem(selected(),true);});wire("rename",[this]{renameEntry();});
 wire("delete_trash",[this]{deleteEntry(false);});wire("delete_perm",[this]{deleteEntry(true);});wire("properties",[this]{properties();});
 wire("cut",[this]{clipSet("cut");});wire("copy",[this]{clipSet("copy");});wire("paste",[this]{paste();});wire("select_all",[this]{list->selectAll();});
 wire("toggle_hidden",[this]{hidden=actions["toggle_hidden"]->isChecked();reload();});
 wire("open_terminal",[this]{launch("terminal");});wire("open_monitoring",[this]{launch("monitoring");});wire("exit",[this]{close();});
 wire("about",[this]{QMessageBox::about(this,"О программе",QString(cfg::ABOUT_TEXT_FILEMANAGER).replace("Python + PyQt5","C++ + Qt"));});wire("hotkeys",[this]{hotkeys();});wire("removable",[this]{removable();});updateNav();
}
void filemanager_func::error(QString s){QMessageBox::critical(this,"Суперапп",s);}void filemanager_func::info(QString s){QMessageBox::information(this,"Суперапп",s);}
void filemanager_func::journal(QString action,QString details){QFile f(cfg::journalPath());if(f.open(QIODevice::Append|QIODevice::Text))f.write((QDateTime::currentDateTime().toString("yyyy-MM-dd HH:mm:ss")+"  "+action.leftJustified(10,' ')+"  "+details+"\n").toUtf8());}
QString filemanager_func::currentDir()const{return activeDir.isEmpty()?normal(cfg::superappRoot()):activeDir;}
// Paths are an application namespace, not an OS-wide filesystem browser.
// Removable media are explicitly added as extra namespace roots.
bool filemanager_func::allowedPath(const QString& path) const {
 auto resolved=[](const QString& p){
  QFileInfo info(p);
  QString canonical=info.canonicalFilePath();
  return normal(canonical.isEmpty()?p:canonical);
 };
 QString candidate=resolved(path);
 auto inside=[&](const QString& root){
  QString r=resolved(root);
  return candidate==r || candidate.startsWith(r+"/");
 };
 if(inside(cfg::superappRoot()))return true;
 for(const auto& root:removableRoots)if(inside(root))return true;
 return false;
}
bool filemanager_func::topLevelRoot(const QString& path) const {
 QString p=normal(path);
 if(p==normal(cfg::superappRoot()))return true;
 for(const auto& root:removableRoots)if(p==normal(root))return true;
 return false;
}
QListWidgetItem* filemanager_func::selected()const{auto a=list->selectedItems();return a.isEmpty()?nullptr:a.first();}
bool filemanager_func::protectedItem(QListWidgetItem*i)const{return i&&i->data(cfg::FILEMANAGER_ROLE_PROTECTED).toBool();}
bool filemanager_func::navigate(QString path,bool pushHistory){path=normal(path);
 // No parent directories above SUPERAPP_ROOT exist from the app's perspective.
 // This check also applies to manual path entry, history and symlink traversal.
 if(!allowedPath(path))return false;
 if(!QFileInfo::exists(path)){error(cfg::format(cfg::MSG_NO_SUCH_PATH,"path",path));return false;}
 if(!QFileInfo(path).isDir()){error(cfg::format(cfg::MSG_NOT_A_DIR,"path",path));return false;}
 activeDir=path;
 pathBar->setText(path);if(pushHistory){history=history.mid(0,historyPos+1);if(history.isEmpty()||history.last()!=path){history<<path;historyPos=history.size()-1;}}journal("visit","переход в каталог: "+path);populate(path);updateNav();return true;}
void filemanager_func::updateNav(){actions["back"]->setEnabled(historyPos>0);actions["forward"]->setEnabled(historyPos+1<history.size());actions["up"]->setEnabled(!activeDir.isEmpty()&&!topLevelRoot(currentDir()));}
void filemanager_func::reload(){if(!activeDir.isEmpty())populate(currentDir());}
void filemanager_func::populate(QString path){list->currentDir=path;list->clear();QDir d(path);if(!d.isReadable()){error(cfg::format(cfg::MSG_OPEN_ERROR,"name",path));return;}
 QDir::Filters filters = QDir::AllEntries | QDir::NoDotAndDotDot | QDir::System;
 if (hidden) filters |= QDir::Hidden;
 auto entries=d.entryInfoList(filters,QDir::NoSort);
 std::sort(entries.begin(),entries.end(),[](const QFileInfo&a,const QFileInfo&b){if(a.isDir()!=b.isDir())return a.isDir();return a.fileName().toLower()<b.fileName().toLower();});
 for(auto e:entries){auto*i=new QListWidgetItem(e.isDir()?folderIcon:fileIcon,e.fileName());i->setData(cfg::FILEMANAGER_ROLE_PATH,e.absoluteFilePath());i->setData(cfg::FILEMANAGER_ROLE_KIND,e.isDir()?"dir":"file");i->setData(cfg::FILEMANAGER_ROLE_PROTECTED,e.fileName()==cfg::SYSTEM_FOLDER);list->addItem(i);}}
void filemanager_func::createEntry(bool dir){bool ok=false;QString name=QInputDialog::getText(this,dir?"Новая папка":"Новый файл",dir?"Имя папки:":"Имя файла:",QLineEdit::Normal,"",&ok).trimmed();if(!ok||name.isEmpty())return;
 if(name=="."||name==".."||name.contains('/')||name.contains(QChar::Null)){error(cfg::format(cfg::MSG_BAD_NAME,"name",name));return;}
 if(name==cfg::SYSTEM_FOLDER||name==cfg::TRASH_FOLDER){error(cfg::format(cfg::MSG_PROTECTED_NAME,"name",name));return;}
 QString target=currentDir()+"/"+name;if(QFileInfo::exists(target)){error(cfg::format(cfg::MSG_EXISTS,"name",name));return;}
 bool saved=dir?QDir().mkdir(target):([](QString p){QFile f(p);return f.open(QIODevice::WriteOnly|QIODevice::NewOnly);})(target);
 if(!saved){error(cfg::format(cfg::MSG_CREATE_FAIL,"name",name));return;}journal("create",(dir?"создан каталог: ":"создан файл: ")+target);reload();}
void filemanager_func::renameEntry(){auto*i=selected();if(!i){info(cfg::MSG_NO_SELECTION);return;}if(protectedItem(i)){error(cfg::format(cfg::MSG_SYSTEM_PROTECTED,"name",i->text()));return;}
 bool ok=false;QString name=QInputDialog::getText(this,"Переименование","Новое имя для «"+i->text()+"»:",QLineEdit::Normal,i->text(),&ok).trimmed();if(!ok||name.isEmpty()||name==i->text())return;
 if(name==cfg::SYSTEM_FOLDER||name==cfg::TRASH_FOLDER){error(cfg::format(cfg::MSG_PROTECTED_NAME,"name",name));return;}
 if(name.contains('/')||name==".."||name=="."){error(cfg::format(cfg::MSG_BAD_NAME,"name",name));return;}
 QString src=i->data(cfg::FILEMANAGER_ROLE_PATH).toString(),dst=currentDir()+"/"+name;if(QFileInfo::exists(dst)){error(cfg::format(cfg::MSG_EXISTS,"name",name));return;}
 if(!QDir().rename(src,dst)){error(cfg::format(cfg::MSG_RENAME_FAIL,"name",i->text()));return;}journal("rename",src+" -> "+dst);reload();}
void filemanager_func::deleteEntry(bool permanent){auto*i=selected();if(!i){info(cfg::MSG_NO_SELECTION);return;}QString name=i->text();if(protectedItem(i)){error(cfg::format(cfg::MSG_SYSTEM_PROTECTED,"name",name));return;}
 QString src=i->data(cfg::FILEMANAGER_ROLE_PATH).toString();if(permanent&&QMessageBox::question(this,"Удаление",cfg::format(cfg::MSG_DELETE_CONFIRM,"name",name))!=QMessageBox::Yes)return;
 bool ok;if(permanent)ok=removeTree(src);else{QDir().mkpath(cfg::trashPath());ok=moveTree(src,uniqueDst(cfg::trashPath()+"/"+name));}
 if(!ok){error(cfg::format(permanent?cfg::MSG_DELETE_FAIL:cfg::MSG_TRASH_FAIL,"name",name));return;}journal(permanent?"delete":"trash",src);reload();}
void filemanager_func::properties(){auto*i=selected();if(!i){info(cfg::MSG_NO_SELECTION);return;}QString path=i->data(cfg::FILEMANAGER_ROLE_PATH).toString();QFileInfo f(path);qint64 size=f.size();int files=0;if(f.isDir()){size=0;QDirIterator it(path,QDir::Files|QDir::NoSymLinks|QDir::Hidden,QDirIterator::Subdirectories);while(it.hasNext()){it.next();size+=it.fileInfo().size();files++;}}
 QString out=(f.isDir()?"Папка: ":"Файл: ")+f.fileName()+"\n\nПуть: "+path+"\nРазмер: "+humanSize(size)+" ("+QString::number(size)+" байт)\nИзменён: "+f.lastModified().toString("yyyy-MM-dd HH:mm:ss");if(f.isDir())out+="\nОбъектов внутри: "+QString::number(files);info(out);}
void filemanager_func::clipSet(QString op){auto items=list->selectedItems();if(items.isEmpty()){info(cfg::MSG_NO_SELECTION);return;}clipboard.clear();for(auto*i:items)if(!protectedItem(i))clipboard<<qMakePair(op,i->data(cfg::FILEMANAGER_ROLE_PATH).toString());}
void filemanager_func::paste(){bool cut=false;for(auto [op,src]:clipboard){if(!QFileInfo::exists(src))continue;QString dst=uniqueDst(currentDir()+"/"+QFileInfo(src).fileName());if(normal(src)==normal(currentDir()+"/"+QFileInfo(src).fileName()))continue;
 bool ok=op=="cut"?moveTree(src,dst):copyTree(src,dst);if(!ok){error(cfg::format(cfg::MSG_PASTE_FAIL,"name",QFileInfo(src).fileName()));continue;}journal(op=="cut"?"move":"copy",src+" -> "+dst);if(op=="cut")cut=true;}
 if(cut)clipboard.clear();reload();}
void filemanager_func::dropped(QStringList paths,QString target,bool internal){target=normal(target);if(!allowedPath(target))return;QString sys=normal(cfg::appRoot());if(target==sys||target.startsWith(sys+"/")){error(cfg::MSG_DND_DROP_SYSTEM);return;}
 for(auto src:paths){src=normal(src);QString name=QFileInfo(src).fileName();if(internal&&(name==cfg::SYSTEM_FOLDER||name==cfg::TRASH_FOLDER))continue;if(!QFileInfo::exists(src)||src==target||QFileInfo(src).dir().absolutePath()==target&&internal||target.startsWith(src+"/"))continue;
 QString dst=uniqueDst(target+"/"+name);bool ok=internal?moveTree(src,dst):copyTree(src,dst);if(!ok){error(cfg::format(cfg::MSG_DND_MOVE_FAIL,"name",name));continue;}journal(internal?"dnd-move":"dnd-copy",src+" -> "+dst);}reload();}
void filemanager_func::search(){bool ok=false;QString needle=QInputDialog::getText(this,"Поиск","Что искать (часть имени):",QLineEdit::Normal,"",&ok).trimmed();if(!ok||needle.isEmpty())return;
 QStringList found;QDirIterator it(cfg::superappRoot(),QDir::AllEntries|QDir::NoDotAndDotDot|QDir::Hidden,QDirIterator::Subdirectories);
 while(it.hasNext()){QString p=it.next();if(p==cfg::appRoot()||p.startsWith(cfg::appRoot()+"/"))continue;if(QFileInfo(p).fileName().contains(needle,Qt::CaseInsensitive))found<<p;}
 QDialog d(this);d.setWindowTitle(QString("Поиск: «%1» — найдено %2").arg(needle).arg(found.size()));d.resize(520,360);auto*lay=new QVBoxLayout(&d);lay->addWidget(new QLabel("Двойной клик по папке — перейти к ней."));auto*lw=new QListWidget;lay->addWidget(lw);auto*btn=new QDialogButtonBox(QDialogButtonBox::Close);connect(btn,&QDialogButtonBox::rejected,&d,&QDialog::reject);lay->addWidget(btn);
 for(auto p:found){auto*i=new QListWidgetItem(QFileInfo(p).isDir()?folderIcon:fileIcon,p);i->setData(Qt::UserRole,p);lw->addItem(i);}connect(lw,&QListWidget::itemDoubleClicked,&d,[&,this](QListWidgetItem*i){QString p=i->data(Qt::UserRole).toString();if(QFileInfo(p).isDir()&&navigate(p))d.accept();});d.exec();}
void filemanager_func::openItem(QListWidgetItem*i,bool popup){if(!i){info(cfg::MSG_NO_SELECTION);return;}QString path=i->data(cfg::FILEMANAGER_ROLE_PATH).toString();if(protectedItem(i)){error(cfg::format(cfg::MSG_SYSTEM_PROTECTED,"name",i->text()));return;}
 if(QFileInfo(path).isDir()){if(popup||(QApplication::keyboardModifiers()&Qt::ControlModifier))launch("popup",{"--folder",path});else navigate(path);}else if(popup){info(cfg::format(cfg::MSG_NOT_A_DIR,"path",path));}else QDesktopServices::openUrl(QUrl::fromLocalFile(path));}
void filemanager_func::launch(QString mode,QStringList args){QString exe=cfg::siblingExecutable(mode);if(!QFileInfo::exists(exe)||!QProcess::startDetached(exe,args))error("Не удалось открыть новое окно: "+exe);}
void filemanager_func::removable(){QFile mounts("/proc/mounts");QStringList devices;if(mounts.open(QIODevice::ReadOnly))for(auto l:QString::fromUtf8(mounts.readAll()).split('\n')){auto f=l.split(' ',Qt::SkipEmptyParts);if(f.size()<3)continue;QString mount=f[1].replace("\\040"," ");QStringList real={"vfat","exfat","ntfs","ntfs3","fuseblk","ext2","ext3","ext4","btrfs","f2fs","xfs","iso9660","udf"};if(real.contains(f[2])&&(mount.startsWith("/media/")||mount.startsWith("/run/media/")||mount.startsWith("/mnt/")||f[0].startsWith("/dev/mmcblk")||f[0].startsWith("/dev/usb")))devices<<mount;}
 removableRoots=QSet<QString>(devices.begin(),devices.end());if(devices.isEmpty()){error(cfg::MSG_NO_REMOVABLE);return;}QDialog d(this);d.setWindowTitle("Съёмные носители");auto*l=new QVBoxLayout(&d);l->addWidget(new QLabel("Подключённые съёмные носители.\nДвойной клик — открыть в основном окне:"));auto*w=new QListWidget;l->addWidget(w);w->addItems(devices);connect(w,&QListWidget::itemDoubleClicked,&d,[&](QListWidgetItem*i){if(navigate(i->text()))d.accept();});d.exec();}
void filemanager_func::hotkeys(){info("F1 — Горячие клавиши\nCtrl+Shift+N — Создать папку\nCtrl+Shift+F — Создать файл\nCtrl+F — Поиск\nCtrl+M — Мониторинг процессов\nF4 — Терминал\nCtrl+X/C/V — Вырезать/Копировать/Вставить\nF2 — Переименовать\nDelete / Shift+Delete — Корзина / Удаление\nF5 — Обновить\nCtrl+H — Скрытые файлы\nAlt+Left/Right/Up — Навигация");}
