import sys
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTabWidget, QToolBar, QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction

APP_NAME = "Adult Video Sidebar Desktop"
SITES = [
    ("SpecialLinks", "https://mrjohndowe.com/.specialLinks/"),
    ("RedTube", "https://www.redtube.com/"),
    ("Pornhub", "https://www.pornhub.com/"),
    ("XVideos", "https://www.xvideos.com/"),
    ("XFree", "https://www.xfree.com/"),
    ("XXXFollow", "https://www.xxxfollow.com/"),
]

class BrowserTab(QWidget):
    def __init__(self, url=None):
        super().__init__()
        layout=QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        self.web=QWebEngineView()
        layout.addWidget(self.web)
        if url: self.web.setUrl(QUrl(url))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 820)
        self.setStyleSheet("""
          QMainWindow,QWidget { background:#111016; color:#f4f0f7; }
          QPushButton { background:#241e29; border:1px solid #3a3040; border-radius:8px; padding:8px 12px; color:#ddd; }
          QPushButton:hover { border-color:#e83b82; background:#30202e; }
          QLineEdit { background:#211c26; border:1px solid #403447; border-radius:8px; padding:9px; color:#fff; }
          QTabWidget::pane { border:1px solid #332a39; }
          QTabBar::tab { background:#201b25; padding:10px 18px; border:1px solid #332a39; }
          QTabBar::tab:selected { background:#632044; color:white; }
          QToolBar { background:#17131b; border:0; spacing:5px; padding:6px; }
          QLabel#brand { font-size:16px; font-weight:800; letter-spacing:2px; color:#f05a9a; }
        """)
        central=QWidget(); self.setCentralWidget(central)
        outer=QVBoxLayout(central); outer.setContentsMargins(10,10,10,10); outer.setSpacing(8)

        header=QHBoxLayout()
        brand=QLabel("▶  ADULT VIDEO SIDEBAR"); brand.setObjectName("brand")
        header.addWidget(brand); header.addStretch()
        header.addWidget(QLabel("Private desktop browser"))
        outer.addLayout(header)

        shortcuts=QHBoxLayout()
        for name,url in SITES:
            b=QPushButton(name); b.clicked.connect(lambda checked=False,u=url,n=name:self.open_site(u,n))
            shortcuts.addWidget(b)
        shortcuts.addStretch()
        outer.addLayout(shortcuts)

        nav=QHBoxLayout()
        self.address=QLineEdit(); self.address.setPlaceholderText("Enter website URL…")
        self.address.returnPressed.connect(self.navigate)
        go=QPushButton("GO"); go.clicked.connect(self.navigate)
        back=QPushButton("‹ Back"); back.clicked.connect(lambda:self.current_web().back())
        forward=QPushButton("Forward ›"); forward.clicked.connect(lambda:self.current_web().forward())
        reloadb=QPushButton("↻ Reload"); reloadb.clicked.connect(lambda:self.current_web().reload())
        newtab=QPushButton("+ New tab"); newtab.clicked.connect(lambda:self.add_tab("https://www.pornhub.com/"))
        for w in [back,forward,reloadb,self.address,go,newtab]: nav.addWidget(w)
        outer.addLayout(nav)

        self.tabs=QTabWidget(); self.tabs.setTabsClosable(True); self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_address)
        outer.addWidget(self.tabs,1)
        self.add_tab("https://www.pornhub.com/")
        self.statusBar().showMessage("Ready — sites open as top-level pages in Chromium WebEngine, not iframe embeds.")

    def add_tab(self,url,title="New tab"):
        tab=BrowserTab(url); i=self.tabs.addTab(tab,title); self.tabs.setCurrentIndex(i)
        tab.web.titleChanged.connect(lambda t,tab=tab:self.update_tab_title(tab,t))
        tab.web.urlChanged.connect(lambda u,tab=tab:self.update_address(tab,u))
        tab.web.loadStarted.connect(lambda:self.statusBar().showMessage("Loading…"))
        tab.web.loadFinished.connect(lambda ok:self.statusBar().showMessage("Loaded" if ok else "Load failed / site may restrict this browser"))
        return tab

    def update_tab_title(self,tab,title):
        i=self.tabs.indexOf(tab)
        if i>=0: self.tabs.setTabText(i,(title or "Page")[:24])

    def update_address(self,tab,url):
        if tab is self.tabs.currentWidget(): self.address.setText(url.toString())

    def current_web(self):
        tab=self.tabs.currentWidget()
        if tab is None: return None
        return tab.web

    def navigate(self):
        raw=self.address.text().strip()
        if not raw: return
        if "://" not in raw: raw="https://"+raw
        self.current_web().setUrl(QUrl(raw))

    def open_site(self,url,name):
        self.add_tab(url,name)

    def sync_address(self,index):
        web=self.current_web()
        if web: self.address.setText(web.url().toString())

    def close_tab(self,index):
        if self.tabs.count()==1:
            self.tabs.widget(0).web.setUrl(QUrl("about:blank")); self.tabs.setTabText(0,"New tab")
        else:
            widget=self.tabs.widget(index); self.tabs.removeTab(index); widget.deleteLater()

def main():
    app=QApplication(sys.argv); app.setApplicationName(APP_NAME)
    win=MainWindow(); win.show()
    sys.exit(app.exec())

if __name__=="__main__": main()
