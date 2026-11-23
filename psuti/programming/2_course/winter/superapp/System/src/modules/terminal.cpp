#include "terminal.h"
#include "settings.h"
#include <QDirIterator>
#include <QFileInfo>
#include <QProcess>
#include <QRegularExpression>
#include <QTextCharFormat>
#include <QTextCursor>
#include <QTimer>
#include <QtWidgets>
#include <csignal>
#include <cstring>
#include <errno.h>
#include <pwd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
namespace {
QString err() { return QString::fromLocal8Bit(strerror(errno)); }
QString readFile(QString path) {
  QFile f(path);
  if (f.open(QIODevice::ReadOnly))
    return QString::fromUtf8(f.readAll());
  return {};
}
bool copyRecursive(QString src, QString dst) {
  QFileInfo f(src);
  if (f.isFile())
    return QFile::copy(src, dst);
  if (!f.isDir() || !QDir().mkpath(dst))
    return false;
  QDir d(src);
  for (auto e : d.entryInfoList(QDir::AllEntries | QDir::NoDotAndDotDot |
                                QDir::Hidden | QDir::System))
    if (!copyRecursive(e.absoluteFilePath(), dst + "/" + e.fileName()))
      return false;
  return true;
}
QStringList
parseCommand(const QString &line) { // shell-like quoting for builtins
  QStringList out;
  QString token;
  QChar quote;
  bool escaped = false, started = false;
  for (auto c : line) {
    if (escaped) {
      token += c;
      escaped = false;
      started = true;
      continue;
    }
    if (c == '\\' && quote != '\'') {
      escaped = true;
      continue;
    }
    if (quote != QChar()) {
      if (c == quote) {
        quote = QChar();
        continue;
      }
      token += c;
      continue;
    }
    if (c == '\'' || c == '"') {
      quote = c;
      started = true;
      continue;
    }
    if (c.isSpace()) {
      if (started) {
        out << token;
        token.clear();
        started = false;
      }
    } else {
      token += c;
      started = true;
    }
  }
  if (started)
    out << token;
  return out;
}
QString userName(uid_t uid) {
  auto *p = getpwuid(uid);
  return p ? QString::fromLocal8Bit(p->pw_name) : QString::number(uid);
}
QString procStart(qulonglong ticks) {
  double uptime = readFile("/proc/uptime").section(' ', 0, 0).toDouble();
  qint64 boot = QDateTime::currentSecsSinceEpoch() - qint64(uptime);
  return QDateTime::fromSecsSinceEpoch(boot + ticks / sysconf(_SC_CLK_TCK))
      .toString("HH:mm:ss");
}
} // namespace
Console::Console(QWidget *p) : QPlainTextEdit(p) {
  QFont f("Monospace", 11);
  f.setStyleHint(QFont::TypeWriter);
  setFont(f);
  setStyleSheet("QPlainTextEdit{background:#0c0c0c;color:#e6e6e6;border:0;}");
  setUndoRedoEnabled(false);
}
void Console::output(QString s, QString kind) {
  QTextCursor c = textCursor();
  c.movePosition(QTextCursor::End);
  setTextCursor(c);
  QTextCharFormat fmt;
  fmt.setForeground(QColor(kind == "stderr" ? "#FF5555"
                           : kind == "info" ? "#56B4E9"
                           : kind == "help" ? "#F0E442"
                                            : "#e6e6e6"));
  c.insertText(s, fmt);
  setTextCursor(c);
  ensureCursorVisible();
}
void Console::newPrompt() {
  QTextCursor c = textCursor();
  c.movePosition(QTextCursor::End);
  setTextCursor(c);
  if (!toPlainText().isEmpty() && !toPlainText().endsWith('\n'))
    output("\n");
  QTextCharFormat fmt;
  fmt.setForeground(QColor("#7CFC00"));
  c = textCursor();
  c.insertText(prompt, fmt);
  setTextCursor(c);
  inputPos = c.position();
  historyIndex = commands.size();
  ensureCursorVisible();
}
void Console::clearScreen() {
  clear();
  inputPos = 0;
  newPrompt();
}
QString Console::currentInput() const {
  return toPlainText().mid(inputPos).section('\n', 0, 0);
}
void Console::replaceInput(QString s) {
  QTextCursor c = textCursor();
  c.movePosition(QTextCursor::End);
  c.setPosition(inputPos, QTextCursor::KeepAnchor);
  c.insertText(s);
  setTextCursor(c);
}
void Console::keyPressEvent(QKeyEvent *e) {
  if (e->modifiers() & Qt::ControlModifier) {
    if (e->key() == Qt::Key_C) {
      output("^C\n", "info");
      emit interruptRequested();
      return;
    }
    if (e->key() == Qt::Key_L) {
      clearScreen();
      return;
    }
    if (e->key() == Qt::Key_D) {
      if (currentInput().isEmpty())
        emit eofRequested();
      return;
    }
  }
  if (busy) {
    e->accept();
    return;
  }
  if (e->key() == Qt::Key_Return || e->key() == Qt::Key_Enter) {
    QString cmd = currentInput();
    QTextCursor c = textCursor();
    c.movePosition(QTextCursor::End);
    setTextCursor(c);
    output("\n");
    if (!cmd.trimmed().isEmpty())
      commands << cmd;
    historyIndex = commands.size();
    emit commandSubmitted(cmd);
    return;
  }
  if (e->key() == Qt::Key_Up) {
    if (historyIndex > 0) {
      --historyIndex;
      replaceInput(commands[historyIndex]);
    }
    return;
  }
  if (e->key() == Qt::Key_Down) {
    if (historyIndex < commands.size() - 1)
      replaceInput(commands[++historyIndex]);
    else {
      historyIndex = commands.size();
      replaceInput("");
    }
    return;
  }
  if (e->key() == Qt::Key_Tab)
    return;
  if (e->key() == Qt::Key_Home) {
    QTextCursor c = textCursor();
    c.setPosition(inputPos);
    setTextCursor(c);
    return;
  }
  if (e->key() == Qt::Key_Backspace && textCursor().position() <= inputPos)
    return;
  if (e->key() == Qt::Key_Left && textCursor().position() <= inputPos)
    return;
  if (e->key() == Qt::Key_Delete && textCursor().position() < inputPos)
    return;
  if (textCursor().position() < inputPos) {
    QTextCursor c = textCursor();
    c.movePosition(QTextCursor::End);
    setTextCursor(c);
  }
  QPlainTextEdit::keyPressEvent(e);
}
terminal_ui::terminal_ui(QWidget *p) : QMainWindow(p) {
  setWindowTitle(cfg::TERMINAL_TITLE);
  resize(cfg::TERMINAL_SIZE);
  console = new Console;
  setCentralWidget(console);
}
terminal_func::terminal_func(QWidget *p, QString startCwd) : terminal_ui(p) {
  cwd = startCwd.isEmpty() ? cfg::superappRoot() : startCwd;
  if (!QFileInfo(cwd).isDir())
    cwd = cfg::superappRoot();
  auto *m = menuBar()->addMenu("Терминал");
  auto *clear = m->addAction("Очистить");
  clear->setShortcut(QKeySequence("Ctrl+L"));
  connect(clear, &QAction::triggered, console, &Console::clearScreen);
  auto *stop = m->addAction("Прервать (Ctrl+C)");
  stop->setShortcut(QKeySequence("Ctrl+C"));
  connect(stop, &QAction::triggered, this, &terminal_func::interrupt);
  m->addSeparator();
  auto *close = m->addAction("Закрыть");
  close->setShortcut(QKeySequence("Ctrl+W"));
  connect(close, &QAction::triggered, this, &QWidget::close);
  auto *help = menuBar()->addMenu("Справка")->addAction("Справка по командам");
  help->setShortcut(QKeySequence("F1"));
  connect(help, &QAction::triggered, this,
          [this] { console->output(cfg::HELP_TEXT, "help"); });
  connect(console, &Console::commandSubmitted, this, &terminal_func::execute);
  connect(console, &Console::interruptRequested, this,
          &terminal_func::interrupt);
  connect(console, &Console::eofRequested, this, &QWidget::close);
  console->output(cfg::BANNER, "info");
  prompt();
}
QString terminal_func::resolve(QString p) const {
  if (p == "~")
    return cfg::superappRoot();
  if (p.startsWith("~/"))
    p = cfg::superappRoot() + p.mid(1);
  if (QDir::isAbsolutePath(p))
    return QDir::cleanPath(p);
  return QDir::cleanPath(cwd + "/" + p);
}
void terminal_func::renderPrompt() {
  QString shortPath = cwd, root = cfg::superappRoot();
  if (cwd == root)
    shortPath = "~";
  else if (cwd.startsWith(root + "/"))
    shortPath = "~" + cwd.mid(root.length());
  QString s = cfg::TERMINAL_PROMPT_TEMPLATE;
  s.replace("{user}", cfg::TERMINAL_PROMPT_USER)
      .replace("{host}", cfg::TERMINAL_PROMPT_HOST)
      .replace("{cwd}", shortPath);
  console->setPrompt(s);
}
void terminal_func::prompt() {
  renderPrompt();
  console->setBusy(false);
  console->newPrompt();
}
void terminal_func::execute(QString line) {
  QStringList t = parseCommand(line.trimmed());
  if (t.isEmpty()) {
    prompt();
    return;
  }
  QString name = t.takeFirst();
  static const QStringList builtins = {
      "cd",   "pwd",   "ls",      "mkdir", "rmdir",  "cp",     "mv",
      "rm",   "clear", "history", "echo",  "help",   "?",      "exit",
      "quit", "ps",    "kill",    "lsdev", "mounts", "ioports"};
  if (builtins.contains(name)) {
    builtin(name, t);
    if (name != "exit" && name != "quit")
      prompt();
  } else
    external(line);
}
void terminal_func::builtin(QString n, QStringList a) {
  auto out = [this](QString s, QString k = "stdout") { console->output(s, k); };
  auto path = [&](int i) { return resolve(a.value(i)); };
  if (n == "exit" || n == "quit") {
    out(cfg::MSG_EXIT, "info");
    close();
    return;
  }
  if (n == "help" || n == "?") {
    out(cfg::HELP_TEXT, "help");
    return;
  }
  if (n == "clear") {
    console->clear();
    return;
  }
  if (n == "pwd") {
    out(cwd + "\n");
    return;
  }
  if (n == "cd") {
    QString p = a.isEmpty() ? cfg::superappRoot() : path(0);
    if (!QFileInfo::exists(p)) {
      out("cd: нет такого каталога: " + a.value(0) + "\n", "stderr");
      return;
    }
    if (!QFileInfo(p).isDir()) {
      out("cd: " + a.value(0) + " не является каталогом\n", "stderr");
      return;
    }
    cwd = p;
    return;
  }
  if (n == "echo") {
    out(a.join(" ") + "\n");
    return;
  }
  if (n == "history") {
    QStringList h = console->history();
    for (int i = 0; i < h.size(); ++i)
      out(QString("%1  %2\n").arg(i + 1, 4).arg(h[i]));
    if (h.isEmpty())
      out("(история пуста)\n", "info");
    return;
  }
  if (n == "ls") {
    QString target = a.isEmpty() ? cwd : path(0);
    QFileInfo f(target);
    if (!f.exists()) {
      out(n + ": " + target + ": нет такого файла или каталога\n", "stderr");
      return;
    }
    if (f.isFile()) {
      out(f.fileName() + "\n");
      return;
    }
    QDir d(target);
    for (auto fi : d.entryInfoList(QDir::AllEntries | QDir::NoDotAndDotDot |
                                       QDir::Hidden | QDir::System,
                                   QDir::Name))
      out(fi.fileName() + (fi.isDir() ? "/" : "") + "\n");
    return;
  }
  if (n == "mkdir" || n == "rmdir") {
    if (a.isEmpty()) {
      out(n + ": не указан операнд\n", "stderr");
      return;
    }
    for (auto v : a) {
      QString p = resolve(v);
      bool ok = n == "mkdir" ? QDir().mkdir(p) : QDir().rmdir(p);
      if (!ok)
        out(n + ": " + p + ": ошибка операции\n", "stderr");
    }
    return;
  }
  if (n == "cp" || n == "mv") {
    if (a.size() < 2) {
      out(n + ": нужны два аргумента (источник и назначение)\n", "stderr");
      return;
    }
    QString src = path(0), dst = path(1);
    if (QFileInfo(dst).isDir())
      dst += "/" + QFileInfo(src).fileName();
    if (!QFileInfo::exists(src)) {
      out(n + ": " + src + ": нет такого файла или каталога\n", "stderr");
      return;
    }
    if (QFileInfo::exists(dst)) {
      out(n + ": " + dst + ": уже существует\n", "stderr");
      return;
    }
    bool ok = n == "cp"
                  ? copyRecursive(src, dst)
                  : (QDir().rename(src, dst) ||
                     copyRecursive(src, dst) &&
                         (QFileInfo(src).isDir() ? QDir(src).removeRecursively()
                                                 : QFile::remove(src)));
    if (!ok)
      out(n + ": ошибка копирования/перемещения\n", "stderr");
    return;
  }
  if (n == "rm") {
    bool rec = a.removeAll("-r") > 0;
    a.removeAll("-R");
    if (a.isEmpty()) {
      out("rm: не указан операнд\n", "stderr");
      return;
    }
    for (auto v : a) {
      QString p = resolve(v);
      QFileInfo f(p);
      if (!f.exists()) {
        out("rm: " + p + ": нет такого файла или каталога\n", "stderr");
        continue;
      }
      if (f.isDir() && !rec) {
        out("rm: " + p + ": это каталог\n", "stderr");
        continue;
      }
      bool ok = f.isDir() ? QDir(p).removeRecursively() : QFile::remove(p);
      if (!ok)
        out("rm: " + p + ": не удалось удалить\n", "stderr");
    }
    return;
  }
  if (n == "mounts" || n == "ioports") {
    out(readFile(n == "mounts" ? "/proc/mounts" : "/proc/ioports"));
    return;
  }
  if (n == "lsdev") {
    QDir d("/dev");
    for (auto f :
         d.entryInfoList(QDir::System | QDir::AllEntries | QDir::NoDotAndDotDot,
                         QDir::Name)) {
      struct stat st{};
      QByteArray p = f.absoluteFilePath().toLocal8Bit();
      if (::lstat(p.constData(), &st) == 0 &&
          (S_ISCHR(st.st_mode) || S_ISBLK(st.st_mode)))
        out(QString(S_ISCHR(st.st_mode) ? "c " : "b ") + f.fileName() + "\n");
    }
    return;
  }
  if (n == "ps") {
    out("    PID  USER          STAT  START     NAME\n");
    QDir proc("/proc");
    for (auto d : proc.entryList(QDir::Dirs | QDir::NoDotAndDotDot)) {
      bool ok = false;
      int pid = d.toInt(&ok);
      if (!ok)
        continue;
      QString s = readFile("/proc/" + d + "/stat");
      int rp = s.lastIndexOf(')');
      if (rp < 0)
        continue;
      auto rest = s.mid(rp + 2).split(' ', Qt::SkipEmptyParts);
      if (rest.size() < 20)
        continue;
      struct stat st{};
      QByteArray p = ("/proc/" + d).toLocal8Bit();
      if (::stat(p.constData(), &st))
        continue;
      out(QString("%1  %2  %3  %4  %5\n")
              .arg(d, 7)
              .arg(userName(st.st_uid), -12)
              .arg(rest[0], -4)
              .arg(procStart(rest[19].toULongLong()),
                   readFile("/proc/" + d + "/comm").trimmed()));
    }
    return;
  }
  if (n == "kill") {
    if (a.isEmpty()) {
      out("kill: не указан операнд\n", "stderr");
      return;
    }
    bool ok = false;
    int pid = a[0].toInt(&ok);
    int sig = a.size() > 1 ? a[1].toInt() : SIGTERM;
    if (!ok || pid <= 0) {
      out("kill: " + a[0] + ": неверный идентификатор процесса\n", "stderr");
      return;
    }
    if (::kill(pid, sig) != 0)
      out("kill: " + a[0] + ": " + err() + "\n", "stderr");
    else
      out(QString("kill: сигнал %1 отправлен процессу %2\n").arg(sig).arg(pid));
    return;
  }
}
void terminal_func::external(QString line) {
  console->setBusy(true);
  process = new QProcess(this);
  process->setProgram("bash");
  process->setArguments({"-c", line});
  process->setWorkingDirectory(cwd);
  connect(process, &QProcess::readyReadStandardOutput, this, [this] {
    console->output(QString::fromLocal8Bit(process->readAllStandardOutput()));
  });
  connect(process, &QProcess::readyReadStandardError, this, [this] {
    console->output(QString::fromLocal8Bit(process->readAllStandardError()),
                    "stderr");
  });
  auto *p = process;
  timeout = new QTimer(p);
  timeout->setSingleShot(true);
  connect(timeout, &QTimer::timeout, this, [this, p] {
    if (p->state() != QProcess::NotRunning) {
      p->kill();
      console->output("(превышено время ожидания: 30 с)\n", "stderr");
    }
  });
  timeout->start(30000);
  connect(p, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
          this, [this, p](int code, QProcess::ExitStatus) {
            if (code != 0 && p->readAllStandardError().isEmpty())
              console->output(QString("(код возврата: %1)\n").arg(code),
                              "info");
            process = nullptr;
            p->deleteLater();
            prompt();
          });
  connect(p, &QProcess::errorOccurred, this,
          [this, p](QProcess::ProcessError e) {
            if (e == QProcess::FailedToStart) {
              console->output("bash не найден в системе\n", "stderr");
              process = nullptr;
              p->deleteLater();
              prompt();
            }
          });
  p->start();
}
void terminal_func::interrupt() {
  if (process && process->state() != QProcess::NotRunning) {
    process->kill();
    return;
  }
  prompt();
}
