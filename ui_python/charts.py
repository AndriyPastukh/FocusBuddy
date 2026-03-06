import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure




class PieChart(FigureCanvasQTAgg):
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(3.5, 3.5), dpi=100)
        self.fig.patch.set_facecolor('#FFFFFF') 
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def plot(self, data, title):
        self.axes.clear()
        if not data: 
            self.axes.text(0.5, 0.5, "No Data", ha='center', va='center', color='#999')
            self.draw()
            return
        
        labels = [d['name'] for d in data]
        sizes = [int(d['count']) for d in data]
        colors = ['#E8DFF5', '#FCE1E4', '#E2F0CB', '#FFF4E1', '#88A0A8', '#E0C068', '#D45D5D']

        wedges, texts, autotexts = self.axes.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.0f%%', 
            startangle=90,
            pctdistance=0.85, 
            wedgeprops=dict(width=0.4, edgecolor='white')
        )
        
        for text in texts:
            text.set_color('#666')
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')

        self.axes.set_title(title.upper(), fontsize=10, color='#AFAE9D', fontweight='bold', pad=10)
        self.draw()

class LineChart(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 2.5), dpi=100)
        self.fig.patch.set_facecolor('#FFFFFF')
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.15)
        super().__init__(self.fig)

    def plot(self, x_data, y_data, title=""):
        self.axes.clear()
        
        self.axes.grid(True, linestyle='--', alpha=0.3, color='#E0E0E0')
        self.axes.set_facecolor('#FFFFFF')
        
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_color('#E0E0E0')
        self.axes.spines['bottom'].set_color('#E0E0E0')
        
        self.axes.tick_params(axis='x', colors='#888', labelsize=8)
        self.axes.tick_params(axis='y', colors='#888', labelsize=8)

        if not x_data:
            self.axes.text(0.5, 0.5, "No activity yet", ha='center', va='center', color='#CCC')
            self.draw()
            return

        main_color = '#6C5CE7' 
        self.axes.plot(x_data, y_data, color=main_color, marker='o', markersize=4, linewidth=2, label='Score')
        
        self.axes.fill_between(x_data, y_data, color=main_color, alpha=0.2)

        if title:
            self.axes.set_title(title, fontsize=10, color='#383838', fontweight='bold', loc='left')

        self.draw()