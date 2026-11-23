#include "popup.h"
#include <QApplication>
#include <QDir>
#include <cstdio>
int main(int argc, char **argv) {
  QApplication app(argc, argv);
  if (argc >= 3 && QString::fromLocal8Bit(argv[1]) == "--folder") {
    QString p = QString::fromLocal8Bit(argv[2]);
    if (!QDir(p).exists())
      return 2;
    FolderPopupWindow win(p);
    win.show();
    return app.exec();
  }
  if (argc < 3)
    return 2;
  bool ok = false;
  int port = QString::fromLocal8Bit(argv[2]).toInt(&ok);
  if (!ok || port < 1 || port > 65535)
    return 2;
  PopupWindow win(QString::fromLocal8Bit(argv[1]), quint16(port));
  win.connectServer();
  if (!win.isVisible())
    return 3;
  return app.exec();
}
