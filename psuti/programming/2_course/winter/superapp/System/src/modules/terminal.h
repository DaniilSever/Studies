#pragma once
#include <QMainWindow>
#include <QPlainTextEdit>
#include <QProcess>
#include <QTimer>
#include <QStringList>
class Console:public QPlainTextEdit {
 Q_OBJECT
public:
 explicit Console(QWidget*parent=nullptr);
 void setPrompt(QString s){prompt=s;}
 void output(QString s,QString kind="stdout");
 void newPrompt(); void clearScreen();
 QStringList history()const{return commands;}
 void setBusy(bool busy){this->busy=busy;}
signals:
 void commandSubmitted(QString);void interruptRequested();void eofRequested();
protected:
 void keyPressEvent(QKeyEvent*)override;
private:
 QString prompt;QStringList commands;int historyIndex=0;int inputPos=0;bool busy=false;
 void replaceInput(QString text);QString currentInput()const;
};
class terminal_ui:public QMainWindow{
 Q_OBJECT
public:
 explicit terminal_ui(QWidget*parent=nullptr);
protected:
 Console* console;
};
class terminal_func:public terminal_ui{
 Q_OBJECT
public:
 explicit terminal_func(QWidget*parent=nullptr,QString startCwd={});
private:
 QString cwd;QProcess *process=nullptr;QTimer *timeout=nullptr;
 QString resolve(QString p)const;void renderPrompt();void execute(QString line);void builtin(QString name,QStringList args);
 void external(QString cmd);void prompt();void interrupt();
};
