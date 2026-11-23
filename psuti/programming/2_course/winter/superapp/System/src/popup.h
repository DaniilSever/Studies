#pragma once
#include <QFormLayout>
#include <QJsonObject>
#include <QLabel>
#include <QLineEdit>
#include <QMainWindow>
#include <QPlainTextEdit>
#include <QTcpSocket>
class PopupWindow : public QMainWindow {
  Q_OBJECT
public:
  explicit PopupWindow(QString host, quint16 port);
  void connectServer();

private:
  QTcpSocket socket;
  QByteArray buffer;
  QFormLayout *form;
  QLabel *titleLabel, *emptyHint;
  void closeRequested();
  void parse();
  void applyData(QJsonObject data);
};
class FolderPopupWindow : public QMainWindow {
  Q_OBJECT
public:
  explicit FolderPopupWindow(QString path);

private:
  QLineEdit *pathBar;
  QPlainTextEdit *list;
  void showFolder(QString path);
};
