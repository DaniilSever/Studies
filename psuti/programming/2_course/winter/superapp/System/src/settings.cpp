#include "settings.h"
#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
namespace cfg {
QString sourceRoot() { return QStringLiteral(SUPERAPP_SOURCE_ROOT); }
QString appRoot() { return sourceRoot(); }
QString superappRoot() { return QFileInfo(appRoot()).dir().absolutePath(); }
QString assetsDir() {
    QString local=QCoreApplication::applicationDirPath()+"/assets";
    return QDir(local).exists()?local:sourceRoot()+"/src/modules/assets";
}
QString trashPath() { return superappRoot()+"/"+TRASH_FOLDER; }
QString journalPath() { return appRoot()+"/fm_journal.log"; }
QString siblingExecutable(const QString &name) { return QCoreApplication::applicationDirPath()+"/superapp_"+name; }
QString format(QString pattern, const QString &key, const QString &value) { return pattern.replace("{"+key+"}",value); }
}
