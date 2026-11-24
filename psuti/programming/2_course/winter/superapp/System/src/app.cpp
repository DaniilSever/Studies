#include "settings.h"
#include "modules/filemanager.h"
#include <QApplication>
#include <QDir>
#include <QFileInfo>
int main(int argc,char**argv){QApplication app(argc,argv);app.setApplicationName("Суперапп");for(auto n:{cfg::DOCUMENTS_FOLDER,cfg::DOWNLOADS_FOLDER,cfg::PICTURES_FOLDER,cfg::VIDEOS_FOLDER,cfg::PROJECTS_FOLDER,cfg::TRASH_FOLDER})QDir().mkpath(cfg::superappRoot()+"/"+n);filemanager_func win;QString path=argc>1&&QFileInfo(QString::fromLocal8Bit(argv[1])).isDir()?QString::fromLocal8Bit(argv[1]):cfg::superappRoot();win.navigate(path);win.show();return app.exec();}
