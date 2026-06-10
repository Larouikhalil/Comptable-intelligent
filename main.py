from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from fpdf import FPDF
import sqlite3
from datetime import datetime

class MainPOS(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        self.init_db()
        
        # --- TAB: VENTE ---
        th_v = TabbedPanelItem(text='Vente')
        layout_v = BoxLayout(orientation='vertical', padding=10, spacing=5)
        self.spinner = Spinner(text='Choisir Produit', values=self.get_products())
        self.in_client = TextInput(hint_text="Nom du Client")
        self.in_qty = TextInput(hint_text="Quantité")
        btn_sell = Button(text="Valider la Vente", background_color=(0, 0.7, 0, 1))
        btn_sell.bind(on_press=self.show_confirm_popup)
        for w in [self.spinner, self.in_client, self.in_qty, btn_sell]: layout_v.add_widget(w)
        th_v.add_widget(layout_v)
        self.add_widget(th_v)
        
        # --- TAB: AJOUTER ---
        th_a = TabbedPanelItem(text='Ajouter')
        layout_a = BoxLayout(orientation='vertical', padding=10, spacing=5)
        self.in_name = TextInput(hint_text="Nom Produit")
        self.in_buy = TextInput(hint_text="Prix Achat")
        self.in_sell = TextInput(hint_text="Prix Vente")
        self.in_stock = TextInput(hint_text="Stock Initial")
        btn_add = Button(text="Enregistrer Produit", background_color=(0, 0, 0.8, 1))
        btn_add.bind(on_press=self.save_product)
        for w in [self.in_name, self.in_buy, self.in_sell, self.in_stock, btn_add]: layout_a.add_widget(w)
        th_a.add_widget(layout_a)
        self.add_widget(th_a)

    def init_db(self):
        self.conn = sqlite3.connect("store.db")
        self.conn.execute("CREATE TABLE IF NOT EXISTS stock (name TEXT, buy REAL, sell REAL, qty INT)")
        self.conn.commit()

    def save_product(self, instance):
        self.conn.execute("INSERT INTO stock VALUES (?,?,?,?)", (self.in_name.text, float(self.in_buy.text), float(self.in_sell.text), int(self.in_stock.text)))
        self.conn.commit()
        self.spinner.values = self.get_products()

    def get_products(self):
        return [row[0] for row in self.conn.execute("SELECT name FROM stock").fetchall()]

    # نافذة التأكيد الاحترافية
    def show_confirm_popup(self, instance):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f"Confirmer la vente de {self.spinner.text} ?"))
        btn = Button(text="Confirmer & Générer PDF")
        btn.bind(on_press=self.process_sale)
        content.add_widget(btn)
        self.popup = Popup(title="Confirmation", content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def process_sale(self, instance):
        # فاتورة احترافية
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(200, 10, txt="FACTURE OFFICIELLE", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Client: {self.in_client.text}", ln=True)
        pdf.cell(200, 10, txt=f"Produit: {self.spinner.text} | Qté: {self.in_qty.text}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.output(f"Facture_{datetime.now().strftime('%H%M%S')}.pdf")
        self.popup.dismiss()

class SupermarketApp(App):
    def build(self):
        return MainPOS()

if __name__ == '__main__':
    SupermarketApp().run()
