#pragma once
#include <QAction>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QMap>
#include <QPair>
#include <QSet>
class QDropEvent;
class FolderListWidget : public QListWidget {
  Q_OBJECT
public:
  explicit FolderListWidget(QWidget *parent = nullptr);
  void setMovement(QListView::Movement movement);
  QString currentDir;
signals:
  void pathsDropped(QStringList paths, QString target, bool internal);

protected:
  QMimeData *mimeData(const QList<QListWidgetItem *> &items) const override;
  void dragEnterEvent(QDragEnterEvent *) override;
  void dragMoveEvent(QDragMoveEvent *) override;
  void dropEvent(QDropEvent *) override;
};
class filemanager_ui : public QMainWindow {
  Q_OBJECT
public:
  explicit filemanager_ui(QWidget *parent = nullptr);

protected:
  QMap<QString, QAction *> actions;
  FolderListWidget *list;
  QLineEdit *pathBar;
  QIcon folderIcon, fileIcon;
  void contextMenuEvent(QContextMenuEvent *) override;
};
class filemanager_func : public filemanager_ui {
  Q_OBJECT
public:
  explicit filemanager_func(QWidget *parent = nullptr);
  bool navigate(QString path, bool pushHistory = true);

private:
  QStringList history;
  QString activeDir;
  int historyPos = -1;
  bool hidden = false;
  QList<QPair<QString, QString>> clipboard;
  QSet<QString> removableRoots;
  void journal(QString action, QString details);
  void reload();
  void populate(QString path);
  void updateNav();
  QListWidgetItem *selected() const;
  QString currentDir() const;
  bool allowedPath(const QString &path) const;
  bool topLevelRoot(const QString &path) const;
  bool protectedItem(QListWidgetItem *) const;
  void openItem(QListWidgetItem *, bool popup = false);
  void createEntry(bool dir);
  void renameEntry();
  void deleteEntry(bool permanent);
  void properties();
  void clipSet(QString operation);
  void paste();
  void dropped(QStringList paths, QString target, bool internal);
  void search();
  void removable();
  void hotkeys();
  void launch(QString mode, QStringList args = {});
  void error(QString message);
  void info(QString message);
};
