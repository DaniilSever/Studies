#include "modules/monitoring.h"
#include <QApplication>
int main(int argc,char**argv){QApplication app(argc,argv);app.setApplicationName("Суперапп — Мониторинг");monitoring_func win;win.show();return app.exec();}
