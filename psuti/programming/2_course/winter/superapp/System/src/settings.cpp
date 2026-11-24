#include "settings.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>

namespace cfg {
namespace {
// A development build is usually in <project>/build[-name]/. Detect the
// source tree by its files rather than by an absolute compile-time path.
// A deployed build has binaries directly in <root>/System/.
QString detectAppRoot() {
    const QDir executableDir(QCoreApplication::applicationDirPath());
    const QDir parentDir(executableDir.filePath(".."));

    const bool projectSourcesPresent =
        QFileInfo::exists(parentDir.filePath("CMakeLists.txt")) &&
        QFileInfo::exists(parentDir.filePath("src/settings.h"));
    const bool inBuildDirectory =
        executableDir.dirName() == QStringLiteral("build") ||
        executableDir.dirName().startsWith(QStringLiteral("build-"));

    if (inBuildDirectory && projectSourcesPresent)
        return parentDir.absolutePath();

    return executableDir.absolutePath();
}
}

QString sourceRoot() { return appRoot(); }
QString appRoot() { return detectAppRoot(); }
QString superappRoot() { return QDir(appRoot()).absoluteFilePath(".."); }

QString assetsDir() {
    const QDir executableDir(QCoreApplication::applicationDirPath());
    const QString alongsideBinaries = executableDir.filePath("assets");
    if (QDir(alongsideBinaries).exists())
        return alongsideBinaries;

    // Development fallback only; deployed builds ship assets alongside binaries.
    return QDir(appRoot()).filePath("src/modules/assets");
}

QString trashPath() { return QDir(superappRoot()).filePath(TRASH_FOLDER); }
QString journalPath() { return QDir(appRoot()).filePath("fm_journal.log"); }
QString siblingExecutable(const QString &name) {
    return QDir(QCoreApplication::applicationDirPath()).filePath("superapp_" + name);
}
QString format(QString pattern, const QString &key, const QString &value) {
    return pattern.replace("{" + key + "}", value);
}
}
