#include "modules/terminal.h"
#include <QApplication>
int main(int argc, char **argv) {
  QApplication app(argc, argv);
  app.setApplicationName("Суперапп — Терминал");
  terminal_func win;
  win.show();
  return app.exec();
}
