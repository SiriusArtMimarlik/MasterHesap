import json
import math
import os
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton, MDRaisedButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.image import Image
from kivy.clock import Clock

FIYAT_DOSYASI = "masterhesap_tam_hafiza.json"

KV = '''
ScreenManager:
    # 1. AÇILIŞ (İNTRO) EKRANI
    Screen:
        name: "splash"
        MDFloatLayout:
            md_bg_color: 0.08, 0.08, 0.1, 1
            Image:
                source: "intro.png"
                size_hint: 1, 1
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                allow_stretch: True
                keep_ratio: False
                
    # 2. ANA EKRAN (MAVİ BANT VE BUTONLAR UÇURULDU)
    Screen:
        name: "ana_ekran"
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: 0.08, 0.08, 0.1, 1
            padding: ["0dp", "15dp", "0dp", "10dp"] # Üstten hafif boşluk
            
            # --- TERTEMİZ ARAMA KUTUSU VE AYARLAR İKONU ---
            MDBoxLayout:
                size_hint_y: None
                height: "60dp"
                padding: ["15dp", "0dp", "15dp", "10dp"]
                spacing: "15dp"
                
                MDTextField:
                    hint_text: "Kategori Ara (Örn: Mobilya)"
                    mode: "round"
                    fill_color_normal: 0.15, 0.15, 0.18, 1
                    text_color_normal: 0.9, 0.9, 0.9, 1
                    on_text: app.kategori_ara(self.text)
                    
                MDIconButton:
                    icon: "cog"
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    pos_hint: {"center_y": 0.5}
                    on_release: root.current = "ayarlar_ekrani"

            # --- GÜNCELLENEN: HIZLI KAYDIRMA ÇUBUĞU ---
            ScrollView:
                id: ana_scroll
                scroll_type: ['bars', 'content']
                bar_width: "8dp"
                bar_color: 0.8, 0.4, 0.1, 0.9
                bar_inactive_color: 0.4, 0.4, 0.4, 0.5
                smooth_scroll_end: 10
                
                MDBoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: "10dp"
                    spacing: "15dp"
                    
                    MDBoxLayout:
                        id: ana_liste
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: "15dp"

                    # --- LİSTE SONU SADECE KDV ---
                    MDCard:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: "100dp"
                        padding: "15dp"
                        spacing: "15dp"
                        md_bg_color: 0.12, 0.12, 0.15, 1
                        radius: [10]
                        
                        MDLabel:
                            text: "Fatura Ayarları"
                            theme_text_color: "Custom"
                            text_color: 0.2, 0.7, 0.9, 1
                            bold: True
                            size_hint_y: None
                            height: "20dp"
                            
                        MDTextField:
                            id: kdv_orani
                            hint_text: "KDV Oranı (%)"
                            mode: "rectangle"
                            text_color_normal: 0.9, 0.9, 0.9, 1
                            line_color_normal: 0.2, 0.7, 0.9, 1

            # --- İNCE, ŞIK VE YEŞİL BUTONLU ALT PANEL ---
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: "150dp"
                padding: "10dp"
                spacing: "5dp"
                md_bg_color: 0.10, 0.12, 0.15, 1
                
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: "90dp"
                    spacing: "2dp"
                    
                    MDLabel:
                        text: "Malzeme Maliyeti:"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        font_size: "13sp"
                    MDLabel:
                        id: lbl_malzeme
                        text: "0.00 TL"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.9, 0.9, 1
                        halign: "right"
                        font_size: "13sp"
                        
                    MDLabel:
                        text: "İşçilik Maliyeti:"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        font_size: "13sp"
                    MDLabel:
                        id: lbl_iscilik
                        text: "0.00 TL"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.9, 0.9, 1
                        halign: "right"
                        font_size: "13sp"
                        
                    MDLabel:
                        text: "KDV Tutarı:"
                        theme_text_color: "Custom"
                        text_color: 0.7, 0.7, 0.7, 1
                        font_size: "13sp"
                    MDLabel:
                        id: lbl_kdv
                        text: "0.00 TL"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.4, 0.4, 1
                        halign: "right"
                        font_size: "13sp"
                        
                    MDLabel:
                        text: "GENEL TOPLAM:"
                        theme_text_color: "Custom"
                        text_color: 0.2, 0.9, 0.4, 1
                        bold: True
                        font_size: "15sp"
                    MDLabel:
                        id: genel_toplam
                        text: "0.00 TL"
                        theme_text_color: "Custom"
                        text_color: 0.2, 0.9, 0.4, 1
                        font_style: "H6"
                        bold: True
                        halign: "right"

                MDFillRoundFlatButton:
                    text: "HESAPLA"
                    font_size: "16sp"
                    size_hint_x: 1
                    size_hint_y: None
                    height: "45dp"
                    md_bg_color: 0.2, 0.6, 0.3, 1  # İSTEDİĞİN YEŞİL TON
                    on_release: app.hesapla()

    # 3. GİZLİ AYARLAR EKRANI (BUTONLAR BURAYA GELDİ)
    Screen:
        name: "ayarlar_ekrani"
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: 0.08, 0.08, 0.1, 1

            MDTopAppBar:
                title: "Gizli Ticari Ayarlar"
                left_action_items: [["arrow-left", lambda x: app.ana_ekrana_don()]]
                md_bg_color: 0.15, 0.45, 0.65, 1
                elevation: 3
                
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"
                
                MDCard:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: "130dp"
                    padding: "20dp"
                    spacing: "15dp"
                    md_bg_color: 0.12, 0.12, 0.15, 1
                    radius: [10]
                    
                    MDLabel:
                        text: "Kâr Marjı Tanımlama"
                        theme_text_color: "Custom"
                        text_color: 0.9, 0.7, 0.2, 1
                        bold: True
                        
                    MDTextField:
                        id: kar_marji_gizli
                        hint_text: "Kâr Marjı (%)"
                        mode: "rectangle"
                        text_color_normal: 0.9, 0.9, 0.9, 1
                        line_color_normal: 0.9, 0.7, 0.2, 1
                        
                # KAYDET VE SIFIRLA BUTONLARI ARTIK BURADA!
                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: "15dp"
                    size_hint_y: None
                    height: "50dp"
                    
                    MDRaisedButton:
                        text: "Hafızaya Kaydet"
                        size_hint_x: 1
                        md_bg_color: 0.2, 0.6, 0.3, 1
                        on_release: 
                            app.verileri_kaydet()
                            app.ana_ekrana_don()
                            
                    MDRaisedButton:
                        text: "Hafızayı Sıfırla"
                        size_hint_x: 1
                        md_bg_color: 0.8, 0.2, 0.2, 1
                        on_release: 
                            app.verileri_sifirla()
                            app.ana_ekrana_don()
                            
                Widget: 
'''

class MasterHesapApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        
        # UYGULAMA İKONUNU BURADA TANIMLIYORUZ
        self.icon = 'logo.png' 
        
        # [A] işareti olanlar "Ayarlar/Çarpanlar"... (Senin kategoriler sözlüğün ve kodların burada aynen duruyor)
        self.kategoriler = {
            "1. KABA İNŞAAT": [
                {"id": "kirim_malzeme", "baslik": "Kırım Malzemesi", "g": ["Kırılacak Hacim m3", "[F]Çuval Atım Tutar", "[A]1 m3 Kaç Çuval (V:60)", "[A]1 m3 Kaç Ton (V:1.5)"]},
                {"id": "kazim_eks", "baslik": "Kazım Ekskavatör (Zemin -> 1:Yumuşak | 2:Sert | 3:Kaya)", "g": ["Alan m2", "Derinlik m", "Zemin Tipi (1,2,3)", "[F]Saatlik Tutar", "[A]Yumuşak m3/Saat(V:50)", "[A]Sert m3/Saat(V:20)", "[A]Kaya m3/Saat(V:10)"]},
                {"id": "drenaj", "baslik": "Drenaj İşlemi", "g": ["Alan m2", "[F]m2 Tutar"]},
                {"id": "fosseptik", "baslik": "Fosseptik", "g": ["Hacim m3", "[F]m3 Tutar"]},
                {"id": "beton", "baslik": "Beton & Demir", "g": ["Beton m3", "[F]Beton m3 Tutar", "[F]Demir kg Tutar", "[A]1m3 Betona Demir(V:100kg)"]},
                {"id": "kalip", "baslik": "Kalıp İşlemi", "g": ["Alan m2", "[F]m2 Tutar"]},
                {"id": "tas_duvar", "baslik": "Taş Duvar", "g": ["Hacim m3", "[F]Taş m3 Tutar", "[F]Çimento(50kg) Tutar", "[F]Kum(Çuval) Tutar", "[F]Kireç(Torba) Tutar", "[A]1m3 Taşa Çimnt(V:4)", "[A]1m3 Taşa Kum(V:15)", "[A]1m3 Taşa Kireç(V:1)"]},
                {"id": "gazbeton", "baslik": "Gazbeton Duvar", "g": ["5'lik Alan m2", "[F]5'lik Adet Tutar", "10'luk Alan m2", "[F]10'luk Adet Tutar", "20'lik Alan m2", "[F]20'lik Adet Tutar", "[F]Örgü Tutkal(25kg) Tutar", "[A]1m2 Gazbeton Adeti(V:7)", "[A]1m2 Tutkal kg(V:4)"]},
                {"id": "tugla", "baslik": "Tuğla Duvar", "g": ["8.5luk Alan m2", "[F]8.5luk Adet Tutar", "13.5luk Alan m2", "[F]13.5luk Adet Tutar", "19luk Alan m2", "[F]19luk Adet Tutar", "Harç Seç (1:Hazır 2:Şantiye)", "[F]Hazır Harç Tutar", "[F]Çimento Tutar", "[F]Kum Tutar", "[F]Kireç Tutar", "[A]1m2 Harç kg(V:15)", "[A]1m2 8.5luk Adet(V:50)", "[A]1m2 13.5luk Adet(V:40)", "[A]1m2 19luk Adet(V:30)", "[A]Ş.Harcı % Çimento(V:20)", "[A]Ş.Harcı % Kum(V:80)", "[A]1Çim=X Kireç(V:0.5)"]},
                {"id": "sap", "baslik": "Şap Uygulaması (Hazır)", "g": ["Alan m2", "Kalınlık cm", "[F]Hazır Şap(25kg) Tutar", "[A]1m3 Şap Tonaj(V:2000kg)"]},
                {"id": "beton_sap", "baslik": "Beton Şap (Çimento+Kum)", "g": ["Hacim m3", "[F]Çimento(50kg) Tutar", "[F]Kum(25kg) Tutar", "[A]1m3 Şapa Çimnt(V:300kg)", "[A]1m3 Şapa Kum(V:1500kg)"]}
            ],
            "2. ALTYAPI İŞLEMLERİ": [
                {"id": "elektrik", "baslik": "Elektrik İşleri", "g": ["Oda Sayısı", "[F]Priz Tutar", "[F]Sigorta Tutar", "Aydınlatma Adedi", "[F]Aydınlatma Tutar", "Aplik Adedi", "[F]Aplik Tutar", "Anahtar Adedi", "[F]Anahtar Tutar", "İnternet Adedi", "[F]İnternet Tutar", "Anten Adedi", "[F]Anten Tutar", "Led mt", "[F]Led mt Tutar", "Kedi Gözü Ad", "[F]Kedi Gözü Tutar", "[F]Kablo(Top) Tutar", "[F]Ek Gider Toplam Tutar", "[A]Odabaşı Priz(V:3)", "[A]Odabaşı Sig(V:1)", "[A]Odabaşı Kablo(V:0.5)"]},
                {"id": "su", "baslik": "Su Tesisatı", "g": ["Alan m2", "[F]m2 Tutar"]},
                {"id": "dogalgaz", "baslik": "Doğalgaz Tesisatı", "g": ["Oda Sayısı", "Petek mt", "Kombi Adedi", "[F]Kombi Tutar", "[F]Petek mt Tutar", "[F]Tesisat Toplam Tutar"]},
                {"id": "termosifon", "baslik": "Termosifon", "g": ["Adet", "[F]Adet Tutar"]}
            ],
            "3. DOĞRAMALAR": [
                {"id": "pimapen", "baslik": "Pimapen Pencere", "g": ["Winner m2", "[F]Winner Tutar", "Egepen m2", "[F]Egepen Tutar", "Winsa m2", "[F]Winsa Tutar", "Alüminyum m2", "[F]Alüminyum Tutar"]},
                {"id": "kapi", "baslik": "İç Kapılar", "g": ["Lake Ad", "[F]Lake Tutar", "Panel Ad", "[F]Panel   Tutar", "Masif Ad", "[F]Masif Tutar", "Melamin Ad", "[F]Melamin Tutar", "PVC Ad", "[F]PVC Tutar"]},
                {"id": "celik_kapi", "baslik": "Çelik Kapı", "g": ["Villa Ad", "[F]Villa Tutar", "Daire Ad", "[F]Daire Tutar", "Bina Ad", "[F]Bina Tutar"]},
                {"id": "kepenk", "baslik": "Kepenk", "g": ["Otomatik Ad", "[F]Oto. Tutar", "Manuel Ad", "[F]Man. Tutar"]},
                {"id": "cambalkon", "baslik": "Cam Balkon", "g": ["Standart m2", "[F]Std Tutar", "Konfor m2", "[F]Konfor Tutar", "Jaluzi m2", "[F]Jaluzi Tutar"]},
                {"id": "menfez", "baslik": "Menfez", "g": ["Adet", "[F]Adet Tutar"]}
            ],
            "4. KAPLAMALAR": [
                {"id": "parke", "baslik": "Parke", "g": ["Laminant Alan m2", "[A]Laminant Paket m2", "[F]Lam.Paket Tutar", "Lamine Alan m2", "[A]Lamine Paket m2", "[F]Lamine Pkt Tutar", "Masif Alan m2", "[A]Masif Paket m2", "[F]Masif Pkt Tutar", "Süpürgelik mt", "[F]Süpürgelik mt Tutar", "Şilte m2", "[F]Şilte m2 Tutar", "[A]Süp. Boyu(V:2.8m)", "[A]Şilte Rulo(V:15m2)"]},
                {"id": "fayans", "baslik": "Fayans", "g": ["Toplam Alan m2", "Fayans En cm", "Fayans Boy cm", "[F]m2 Tutar", "[F]Kalekim(25kg) Tutar", "[F]Derz(5kg) Tutar", "[F]Derz Artısı(Pk) Tutar", "[A]1m2 Kalekim kg(V:6)"]},
                ],
            "5. İNCE İŞÇİLİK": [
                {"id": "duvar_siva", "baslik": "Duvar Sıva (Alçı/Karışık)", "g": ["Alan m2", "[F]Alçı Torba Tutar", "[F]File(Top) Tutar", "[A]1 Torba Alçı m2(V:3)", "[A]1 Top File mt(V:50)"]},
                {"id": "tavan_siva", "baslik": "Tavan Sıva", "g": ["Alan m2", "[F]Alçı Torba Tutar", "[F]File(Top) Tutar", "[A]1 Torba Alçı m2(V:3)", "[A]1 Top File mt(V:50)"]},
                {"id": "asma_tavan", "baslik": "Asma Tavan", "g": ["Alan m2", "[F]Alçıpan Plk Tutar", "[F]U-Profil Tutar", "[F]C-Profil Tutar", "[F]Derz Bandı Tutar", "[F]Sıva/Alçı Torba Tutar", "[F]Vida/Dübel Tutar", "[A]1 Plk Alçıpan m2(V:3)", "[A]1m2 U-Profil Boy(V:0.3)", "[A]1m2 C-Profil Boy(V:0.8)", "[A]1 Top Bant m2(V:50)", "[A]1 Torba Alçı m2(V:10)", "[A]1 Pkt Vida m2(V:25)"]},
                {"id": "klipin", "baslik": "Klipin Tavan 30x30", "g": ["Alan m2", "[F]Plaka Adet Tutar", "[F]U-C Profil Tutar", "[F]Askı/Yay Tutar", "[F]Vida/Dübel Tutar", "Kare Led Adedi", "[F]Kare Led Tutar"]},
                {"id": "stropiyer", "baslik": "Köşe Straforu", "g": ["Toplam Tavan m2", "[F]Strafor mt Tutar", "[A]Stropiyer Fire(V:1.1)"]},
                {"id": "mantolama", "baslik": "Dış Cephe Mantolama", "g": ["Alan m2", "Yalıtım(1:EPS 2:XPS 3:Taş)", "[F]EPS m2 Tutar", "[F]XPS m2 Tutar", "[F]Taşyünü m2 Tutar", "[F]Yapıştırıcı(25kg) Tutar", "[F]Sıva(25kg) Tutar", "[F]File(Top) Tutar", "[F]Dübel Adet Tutar", "[F]Dek.Sıva(25kg) Tutar", "[A]Yapıştırıcı kg/m2(V:5)", "[A]Sıva kg/m2(V:5)", "[A]File Çarpan(V:1.1)", "[A]Dübel Ad/m2(V:6)", "[A]Dek.Sıva kg/m2(V:3)"]},
                {"id": "ic_boya", "baslik": "İç Cephe Boya", "g": ["Alan m2", "[F]Boya 20L Tutar", "[F]Astar 10L Tutar", "Rulo/Fırça Ad", "[F]Sarf Ad Tutar", "[A]1m2 Boya Lt(V:0.3)", "[A]1m2 Astar Lt(V:0.1)"]},
                {"id": "dis_boya", "baslik": "Dış Cephe Boya", "g": ["Alan m2", "[F]Boya 20L Tutar", "[F]Astar 10L Tutar", "Rulo/Fırça Ad", "[F]Sarf Ad Tutar", "[A]1m2 Boya Lt(V:0.3)", "[A]1m2 Astar Lt(V:0.1)"]}
                ],
            "6. BANYO AKSESUARLARI": [
                {"id": "b_aksesuar", "baslik": "Banyo Donanımları", "g": ["Evye Ad", "[F]Evye Tutar", "Batarya Ad", "[F]Batarya Tutar", "D.Başlık Ad", "[F]D.Başlık Tutar", "D.Batarya Ad", "[F]D.Batarya Tutar"]},
                {"id": "klozet", "baslik": "Klozetler", "g": ["Gömme Ad", "[F]Gömme Tutar", "Duv.Sıfır Ad", "[F]Duv.Sıfır Tutar", "Klasik Ad", "[F]Klasik Tutar", "Alaturka Ad", "[F]Alaturka Tutar"]},
                {"id": "dusakabin", "baslik": "Duşakabin", "g": ["Adet", "[F]Adet Tutar"]}
            ],
            "7. MOBİLYA İMALATI": [
                {"id": "m_olcu", "baslik": "Mobilya Ölçüleri (İhtiyaç Analizi)", "g": ["Gövde Alan m2", "Kapak Alan m2", "[A]Gövde Çarpanı(V:2)", "[A]Kapak Çarpanı(V:1.2)", "[A]Sun/MDF Plk(V:5.88)", "[A]HG/Akr Plk(V:3.41)"]},
                {"id": "m_sun", "baslik": "Suntalam Plaka", "g": ["Kullanılacak Plaka Ad", "[F]Plaka Tutar"]},
                {"id": "m_mdf", "baslik": "MDFlam Plaka", "g": ["Kullanılacak Plaka Ad", "[F]Plaka Tutar"]},
                {"id": "m_hg", "baslik": "HighGloss Plaka", "g": ["Kullanılacak Plaka Ad", "[F]Plaka Tutar"]},
                {"id": "m_akr", "baslik": "Akrilik Plaka", "g": ["Kullanılacak Plaka Ad", "[F]Plaka Tutar"]},
                {"id": "m_lak", "baslik": "Lake Plaka", "g": ["Kullanılacak Plaka Ad", "[F]Plaka Tutar"]},
                {"id": "m_aksesuar", "baslik": "İşçilik ve Aksesuar", "g": ["Kesilecek Plaka Ad", "[F]Kesim(Plk) Tutar", "Bantlama mt", "[F]Bantlama mt Tutar", "Menteşe Ad", "[F]Menteşe Ad Tutar", "Ray Ad", "[F]Ray Ad Tutar", "Kulp Ad", "[F]Kulp Ad Tutar", "Vida Kutu", "[F]Vida Kutu Tutar", "Sürgü Sistem Ad", "[F]Sürgü Ad Tutar", "Amortisör Takım", "[F]Amortisör Tk Tutar", "Ayna mt", "[F]Ayna mt Tutar"]},
                {"id": "m_tez", "baslik": "Tezgah Seçimi", "g": ["Çimstone mt", "[F]Çim.Tutar", "Porselen mt", "[F]Por.Tutar", "Granit mt", "[F]Gra.Tutar", "Corian mt", "[F]Cor.Tutar", "Masif mt", "[F]Mas.Tutar", "Mermer mt", "[F]Mer.Tutar"]},
                {"id": "m_evy", "baslik": "Evye / Batarya", "g": ["Krom Evye Ad", "[F]Krom Tutar", "Granit Evye Ad", "[F]Granit Tutar", "Seramik Evye Ad", "[F]Ser. Tutar", "Batarya Ad", "[F]Batarya Tutar"]}
            ],
            "8. KARKAS & ÇATI": [
                {"id": "karkas", "baslik": "Profil Karkas (Kaynaklı)", "g": ["Toplam Alan m2", "Duvar Toplam Uzunluk m", "Yükseklik m", "Bölücü Duvar Ad", "Kapı Ad", "Pencere Ad", "[F]100x100 Boy(6m) Tutar", "[F]50x100 Boy(6m) Tutar", "[F]Kaynak/Sarf Tutar", "[A]Ana Dikme Ara(V:3m)", "[A]Ara Dikme Adet(V:5)", "[A]Yatay Sıra(V:3)", "[A]Kapı Fire(V:1Boy)", "[A]Penc. Fire(V:2Boy)", "[A]Tavan Boy/m2(V:0.5)"]},
                {"id": "cati", "baslik": "Çatı Sistemi", "g": ["Alan m2", "[F]40x60 Makas Boy(6m) Tutar", "[F]40x40 Aşık Boy(6m) Tutar", "[F]Sandviç Pnl m2 Tutar", "[F]OSB Plaka Tutar", "[F]Membran Rulo Tutar", "[F]Akıllı Vida Tutar", "[A]Makas mt/m2(V:1.2)", "[A]Aşık mt/m2(V:2.0)", "[A]1 OSB m2(V:2.98)", "[A]1 Rulo Membran m2(V:10)", "[A]1 Kutu Vida m2(V:25)"]}
            ],
            "9. ŞAHSİ GİDERLER": [
                {"id": "fatura", "baslik": "Fatura", "g": ["Ay", "[F]Aylık Tutar"]},
                {"id": "reklam", "baslik": "Reklam", "g": ["Ay", "[F]Aylık Tutar"]},
                {"id": "yol", "baslik": "Yol", "g": ["Gün", "[F]Günlük Tutar"]},
                {"id": "yemek", "baslik": "Yemek", "g": ["Gün", "[F]Günlük Tutar"]}
            ],
            "10. GENEL İŞÇİLİK & TAŞERON": [
                {"id": "isc_kirim", "baslik": "Kırım İşlemleri", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_kaz_isci", "baslik": "Kazım İşçi", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_beton", "baslik": "Beton & Demir İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_kalip", "baslik": "Kalıp İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_tas", "baslik": "Taş Duvar İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_duvar", "baslik": "Gazbeton ve Tuğla İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_sap", "baslik": "Şap İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_elektrik", "baslik": "Elektrik İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_su", "baslik": "Su Tesisatı İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_parke", "baslik": "Parke İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_fayans", "baslik": "Fayans İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_dsiva", "baslik": "Duvar Sıva İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_tsiva", "baslik": "Tavan Sıva İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_atavan", "baslik": "Asma & Klipin Tavan İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_discephe", "baslik": "Dış Cephe İskele/İşçilik", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_boya", "baslik": "Boya İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_mobilya", "baslik": "Mobilya İşçiliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_kaynak_d", "baslik": "Kaynak İşçiliği (Duvar)", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_kaynak_c", "baslik": "Kaynak İşçiliği (Çatı)", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_temizlik", "baslik": "Şantiye Temizliği", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_genel", "baslik": "Genel İşçilik", "g": ["Birim", "[F]Tutar"]},
                {"id": "isc_diger", "baslik": "Diğer İşçilik Kalemleri", "g": ["Birim", "[F]Tutar"]}
            ]
        }
        
        # 5. İnce İşçilik, 6. Mutfak, 7. Diğer (İkinci Partta gelecek)
        self.girdi_kutu_ref = {}
        self.sonuc_etiketleri = {}
        self.kategori_toplam_etiketleri = {}
        self.kayitli_veriler = {}
        
        return Builder.load_string(KV)

    def on_start(self):
        self.verileri_yukle()
        self.root.transition = FadeTransition()
        self.ana_liste = self.root.ids.ana_liste
        self.arama_sozlugu = {}

        # Kategorileri listeye çevirip tek tek işleyeceğiz (Telefon boğulmasın diye)
        self.kat_listesi = list(self.kategoriler.items())
        self.suanki_kat_index = 0
        
        # Nefes alan döngüyü başlat
        Clock.schedule_once(self.kategori_ciz, 0.1)

    def kategori_ciz(self, dt):
        # EĞER ÇİZİLECEK KATEGORİ KALMADIYSA UYGULAMAYI AÇ
        if self.suanki_kat_index >= len(self.kat_listesi):
            # Kayıtlı ayarları ekrana yansıt
            if "_fatura_kdv_" in self.kayitli_veriler:
                self.root.ids.kdv_orani.text = str(self.kayitli_veriler["_fatura_kdv_"])
            if "_gizli_kar_" in self.kayitli_veriler:
                self.root.ids.kar_marji_gizli.text = str(self.kayitli_veriler["_gizli_kar_"])
            
            # Arka planda ilk hesaplamayı yap ve ana ekrana atla
            self.hesapla()
            self.root.current = "ana_ekran"
            return
            
        # SADECE SIRADAKİ 1 KATEGORİYİ ÇEK
        kat_adi, kalemler = self.kat_listesi[self.suanki_kat_index]
        
        kat_kart = MDCard(orientation='vertical', padding="10dp", spacing="10dp", md_bg_color=(0.10, 0.12, 0.15, 1), radius=[10], adaptive_height=True)

        # ANA KATEGORİ BAŞLIĞI 
        kat_baslik_satiri = MDBoxLayout(orientation='horizontal', spacing="5dp", size_hint_y=None, height="40dp")
        kat_baslik_lbl = MDLabel(text=kat_adi, theme_text_color="Custom", text_color=(0.9, 0.4, 0.1, 1), bold=True)
        kat_btn = MDIconButton(icon="chevron-down", pos_hint={"center_y": 0.5}, theme_text_color="Custom", text_color=(0.9, 0.4, 0.1, 1))

        kat_baslik_satiri.add_widget(kat_baslik_lbl)
        kat_baslik_satiri.add_widget(kat_btn)
        kat_kart.add_widget(kat_baslik_satiri)

        kat_icerik = MDBoxLayout(orientation='vertical', spacing="10dp", adaptive_height=True)
        kat_alt_toplam_lbl = MDLabel(text="KATEGORİ TOPLAMI: 0.00 TL", theme_text_color="Custom", text_color=(0.2, 0.7, 1, 1), bold=True, halign="right", size_hint_y=None, height="30dp")
        self.kategori_toplam_etiketleri[kat_adi] = kat_alt_toplam_lbl

        # KATEGORİ AÇ/KAPAT
        def ac_kategori(kart=kat_kart, icerik=kat_icerik, alt_toplam=kat_alt_toplam_lbl, btn=kat_btn):
            if icerik not in kart.children:
                kart.remove_widget(alt_toplam)
                kart.add_widget(icerik)
                kart.add_widget(alt_toplam)
                btn.icon = "chevron-up"

        def kapat_kategori(kart=kat_kart, icerik=kat_icerik, btn=kat_btn):
            if icerik in kart.children:
                kart.remove_widget(icerik)
                btn.icon = "chevron-down"

        def toggle_kategori(instance, kart=kat_kart, icerik=kat_icerik, alt_toplam=kat_alt_toplam_lbl, btn=kat_btn):
            if icerik in kart.children: kapat_kategori(kart, icerik, btn)
            else: ac_kategori(kart, icerik, alt_toplam, btn)

        kat_btn.bind(on_release=toggle_kategori)
        kat_arama_adi = kat_adi.replace("İ", "i").replace("I", "ı").lower()
        self.arama_sozlugu[kat_arama_adi] = {"widget": kat_baslik_lbl, "ac_func": ac_kategori}

        # ALT KALEMLER
        for kalem in kalemler:
            kalem_kutu = MDBoxLayout(orientation='vertical', spacing="5dp", padding="0dp", adaptive_height=True)

            baslik_satiri = MDBoxLayout(orientation='horizontal', spacing="5dp", size_hint_y=None, height="40dp")
            lbl_baslik = MDLabel(text=f"• {kalem['baslik']}", theme_text_color="Custom", text_color=(0.7, 0.9, 0.9, 1), font_size="14sp", bold=True, shorten=True, shorten_from="right")
            baslik_satiri.add_widget(lbl_baslik)

            kalem_arama_adi = kalem['baslik'].replace("İ", "i").replace("I", "ı").lower()
            self.arama_sozlugu[kalem_arama_adi] = {"widget": lbl_baslik, "ac_func": ac_kategori}

            girdiler = kalem["g"]
            temel_girdiler = [g for g in girdiler if "[A]" not in g and "[F]" not in g]
            ayar_girdiler = [g for g in girdiler if "[A]" in g or "[F]" in g]

            temel_kutu = MDBoxLayout(orientation='vertical', spacing="5dp", adaptive_height=True)
            for g_adi in temel_girdiler:
                b_id = f"{kalem['id']}_{g_adi}"
                kutu = MDTextField(hint_text=g_adi, mode="rectangle", size_hint_y=None, height="70dp")
                kutu.line_color_normal = (0.5, 0.5, 0.5, 1)
                if b_id in self.kayitli_veriler: kutu.text = str(self.kayitli_veriler[b_id])
                self.girdi_kutu_ref[b_id] = kutu
                temel_kutu.add_widget(kutu)

            ayar_kutu = MDBoxLayout(orientation='vertical', spacing="5dp", adaptive_height=True)
            if ayar_girdiler:
                for g_adi in ayar_girdiler:
                    b_id = f"{kalem['id']}_{g_adi}"
                    temiz_isim = g_adi.replace("[A]", "").replace("[F]", "")
                    kutu = MDTextField(hint_text=temiz_isim, mode="rectangle", size_hint_y=None, height="70dp")
                    if "[F]" in g_adi: kutu.line_color_normal = (0.3, 0.8, 0.3, 1)
                    else: kutu.line_color_normal = (0.8, 0.3, 0.8, 1)
                        
                    if b_id in self.kayitli_veriler: kutu.text = str(self.kayitli_veriler[b_id])
                    self.girdi_kutu_ref[b_id] = kutu
                    ayar_kutu.add_widget(kutu)

                btn_ayar = MDIconButton(icon="chevron-down", pos_hint={"center_y": 0.5})

                def toggle_ayarlar(instance, k_kutu=kalem_kutu, a_kutu=ayar_kutu, btn=btn_ayar):
                    if a_kutu in k_kutu.children:
                        k_kutu.remove_widget(a_kutu)
                        btn.icon = "chevron-down"
                    else:
                        k_kutu.add_widget(a_kutu, index=1)
                        btn.icon = "chevron-up"

                btn_ayar.bind(on_release=toggle_ayarlar)
                baslik_satiri.add_widget(btn_ayar)

            kalem_kutu.add_widget(baslik_satiri)
            kalem_kutu.add_widget(temel_kutu)
            
            sonuc_satiri = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="30dp")
            lbl_detay = MDLabel(text="Hazır...", theme_text_color="Custom", text_color=(0.5, 0.7, 0.5, 1), font_size="12sp", size_hint_x=0.65)
            lbl_ara_toplam = MDLabel(text="0.00 TL", theme_text_color="Custom", text_color=(1, 0.8, 0.2, 1), bold=True, halign="right", size_hint_x=0.35)
            self.sonuc_etiketleri[kalem["id"]] = {"detay": lbl_detay, "toplam": lbl_ara_toplam}
            sonuc_satiri.add_widget(lbl_detay)
            sonuc_satiri.add_widget(lbl_ara_toplam)
            
            kalem_kutu.add_widget(sonuc_satiri)
            kat_icerik.add_widget(kalem_kutu)

        kat_kart.add_widget(kat_alt_toplam_lbl)
        self.ana_liste.add_widget(kat_kart)
        
        # BU KATEGORİ BİTTİ, 0.05 SANİYE NEFES AL VE BİR SONRAKİ KATEGORİYE GEÇ
        self.suanki_kat_index += 1
        Clock.schedule_once(self.kategori_ciz, 0.05)

    def ana_ekrana_don(self):
        self.root.current = "ana_ekran"

    # --- KAYBOLAN VE ŞİMDİ AKILLANDIRILAN ARAMA MOTORU ---
    def kategori_ara(self, kelime):
        # Yazılan kelimeyi küçük harfe çevir
        kelime = kelime.replace("İ", "i").replace("I", "ı").lower()
        if not kelime:
            return
            
        # Hafızadaki TÜM başlıklar içinde kelimeyi ara
        for isim, veri in self.arama_sozlugu.items():
            if kelime in isim:
                # 1. Hedef kategoriyi OTOMATİK AÇ! (Kapalıysa açılır, açıksa öyle kalır)
                veri["ac_func"]()
                
                # 2. Ekranda ilgili yere kaydır (Animasyonun açılması için 0.1 saniye mühlet veriyoruz)
                scroll = self.root.ids.ana_scroll
                Clock.schedule_once(lambda dt, w=veri["widget"]: scroll.scroll_to(w), 0.1)
                break

    def v(self, k_id, g_adi, def_val=0.0):
        benzersiz_id = f"{k_id}_{g_adi}"
        kutu = self.girdi_kutu_ref.get(benzersiz_id)
        if not kutu or not kutu.text: 
            return def_val
        try:
            m = kutu.text.replace(',', '.')
            m = ''.join(c for c in m if c.isdigit() or c == '.')
            parts = m.split('.')
            if len(parts) > 2: m = parts[0] + '.' + ''.join(parts[1:])
            val = float(m) if m else 0.0
            return val if val != 0.0 else def_val
        except: 
            return def_val

    def verileri_kaydet(self):
        # 1. Listedeki normal kutuları kaydet
        for b_id, kutu in self.girdi_kutu_ref.items():
            if kutu.text:
                self.kayitli_veriler[b_id] = kutu.text
            elif b_id in self.kayitli_veriler:
                del self.kayitli_veriler[b_id]
                
        # --- 2. YENİ: TİCARİ AYARLARI KAYDET ---
        if self.root.ids.kdv_orani.text:
            self.kayitli_veriler["_fatura_kdv_"] = self.root.ids.kdv_orani.text
        elif "_fatura_kdv_" in self.kayitli_veriler:
            del self.kayitli_veriler["_fatura_kdv_"]
            
        if self.root.ids.kar_marji_gizli.text:
            self.kayitli_veriler["_gizli_kar_"] = self.root.ids.kar_marji_gizli.text
        elif "_gizli_kar_" in self.kayitli_veriler:
            del self.kayitli_veriler["_gizli_kar_"]

        # 3. Hafıza dosyasına yazdır
        with open(FIYAT_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(self.kayitli_veriler, f, ensure_ascii=False)

    def verileri_yukle(self):
        if os.path.exists(FIYAT_DOSYASI):
            with open(FIYAT_DOSYASI, "r", encoding="utf-8") as f: self.kayitli_veriler = json.load(f)

    def verileri_sifirla(self):
        silinecek_anahtarlar = []
        
        # 1. Sadece "[F]" ve "[A]" İÇERMEYEN (yani gri) kutuları bul ve temizle
        for b_id, kutu in self.girdi_kutu_ref.items():
            if "[F]" not in b_id and "[A]" not in b_id:
                kutu.text = ""  # Ekrandaki yazıyı sil
                silinecek_anahtarlar.append(b_id)
                
        # 2. Hafızadaki sözlükten de bu gri kutuların ölçülerini uçur
        for key in silinecek_anahtarlar:
            if key in self.kayitli_veriler:
                del self.kayitli_veriler[key]
                
        # 3. Geriye kalanları (Yeşil Fiyatları ve Mor Çarpanları) dosyaya tekrar kaydet
        with open(FIYAT_DOSYASI, "w", encoding="utf-8") as f: 
            json.dump(self.kayitli_veriler, f, ensure_ascii=False)
            
        # 4. Ekranı sıfırlanmış haliyle yeniden hesaplat
        self.hesapla()

    def set_res(self, k_id, detay, t):
        # Kâr çarpanını alıp kalemin ham maliyetine şırınga ediyoruz
        kkarli_t = t * getattr(self, 'aktif_kar_carpani', 1.0)
        self.sonuc_etiketleri[k_id]["detay"].text = detay
        self.sonuc_etiketleri[k_id]["toplam"].text = f"{kkarli_t:,.2f} TL"
        return kkarli_t

    def hesapla(self):
        # --- 1. YENİ: KÂR ÇARPANINI EN BAŞTA ÇEKİYORUZ ---
        try:
            kar_orani = float(self.root.ids.kar_marji_gizli.text.replace(',', '.')) if self.root.ids.kar_marji_gizli.text else 0.0
        except:
            kar_orani = 0.0
        self.aktif_kar_carpani = 1.0 + (kar_orani / 100.0)

        genel_toplam = 0.0
        kat_toplamlari = {k:0.0 for k in self.kategoriler.keys()}
        
        # 1. KABA İNŞAAT
        kat = "1. KABA İNŞAAT"
        m8 = self.v("tugla", "8.5luk Alan m2")
        m13 = self.v("tugla", "13.5luk Alan m2")
        m19 = self.v("tugla", "19luk Alan m2")
        
        if (m8 + m13 + m19) > 0:
            harc_kg_m2 = self.v("tugla", "[A]1m2 Harç kg(V:15)", 15)
            harc_secim = self.v("tugla", "Harç Seç (1:Hazır 2:Şantiye)", 1) 
            
            # Dinamik Tuğla Çarpanlarını Çekiyoruz
            c8 = self.v("tugla", "[A]1m2 8.5luk Adet(V:50)", 50)
            c13 = self.v("tugla", "[A]1m2 13.5luk Adet(V:40)", 40)
            c19 = self.v("tugla", "[A]1m2 19luk Adet(V:30)", 30)
            
            # Adet Hesapları
            ad8 = math.ceil(m8 * c8) if m8 > 0 else 0
            ad13 = math.ceil(m13 * c13) if m13 > 0 else 0
            ad19 = math.ceil(m19 * c19) if m19 > 0 else 0
            
            toplam_harc_kg = (m8 + m13 + m19) * harc_kg_m2
            
            harc_maliyeti = 0
            harc_metni = ""
            
            # 1. ŞALTER: HAZIR HARÇ SEÇİLDİYSE
            if harc_secim == 1:
                hazir_torba = math.ceil(toplam_harc_kg / 25)
                harc_maliyeti = hazir_torba * self.v("tugla", "[F]Hazır Harç Tutar")
                harc_metni = f"Hazır Harç: {hazir_torba} Torba"
                
            # 2. ŞALTER: ŞANTİYE HARCI SEÇİLDİYSE
            elif harc_secim == 2:
                # Dinamik karışım oranlarını çekiyoruz (Yüzdeleri matematiksel olarak /100 yapıyoruz)
                yuzde_cimen = self.v("tugla", "[A]Ş.Harcı % Çimento(V:20)", 20) / 100.0
                yuzde_kum = self.v("tugla", "[A]Ş.Harcı % Kum(V:80)", 80) / 100.0
                carpan_kirec = self.v("tugla", "[A]1Çim=X Kireç(V:0.5)", 0.5)
                
                cimen_kg = toplam_harc_kg * yuzde_cimen  
                kum_kg = toplam_harc_kg * yuzde_kum    
                cimen_t = math.ceil(cimen_kg / 50)
                kum_c = math.ceil(kum_kg / 25)
                kirec_t = math.ceil(cimen_t * carpan_kirec)
                
                harc_maliyeti = (cimen_t * self.v("tugla", "[F]Çimento Tutar")) + (kum_c * self.v("tugla", "[F]Kum Tutar")) + (kirec_t * self.v("tugla", "[F]Kireç Tutar"))
                harc_metni = f"Şantiye Harcı: {cimen_t} Çim | {kum_c} Kum | {kirec_t} Kir"
                
            else:
                harc_metni = "Hatalı Seçim! (1 veya 2 yazın)"
                
            tugla_maliyeti = (ad8 * self.v("tugla", "[F]8.5luk Adet Tutar")) + \
                             (ad13 * self.v("tugla", "[F]13.5luk Adet Tutar")) + \
                             (ad19 * self.v("tugla", "[F]19luk Adet Tutar"))
            
            t_toplam = tugla_maliyeti + harc_maliyeti
            
            detay = []
            if m8 > 0: detay.append(f"8.5'luk: {ad8}Ad")
            if m13 > 0: detay.append(f"13.5'luk: {ad13}Ad")
            if m19 > 0: detay.append(f"19'luk: {ad19}Ad")
            
            sonuc_yazisi = " | ".join(detay) + f" => {harc_metni}"
            
            kat_toplamlari[kat] += self.set_res("tugla", sonuc_yazisi, t_toplam)
        else: 
            kat_toplamlari[kat] += self.set_res("tugla", "Girdi Yok", 0)

        b_m3 = self.v("beton", "Beton m3")
        if b_m3 > 0:
            demir = b_m3 * self.v("beton", "[A]1m3 Betona Demir(V:100kg)", 100)
            t_beton = (b_m3 * self.v("beton", "[F]Beton m3 Tutar")) + (demir * self.v("beton", "[F]Demir kg Tutar"))
            kat_toplamlari[kat] += self.set_res("beton", f"Beton: {b_m3}m3 | Demir: {demir}kg", t_beton)
        else: 
            kat_toplamlari[kat] += self.set_res("beton", "Girdi Yok", 0)
        
        dr_m2 = self.v("drenaj", "Alan m2")
        if dr_m2 > 0:
            t_dr = dr_m2 * self.v("drenaj", "[F]m2 Tutar")
            kat_toplamlari[kat] += self.set_res("drenaj", "Drenaj İşlemi", t_dr)
        else: kat_toplamlari[kat] += self.set_res("drenaj", "Girdi Yok", 0)
        
        f_m3 = self.v("fosseptik", "Hacim m3")
        if f_m3 > 0:
            t_fos = f_m3 * self.v("fosseptik", "[F]m3 Tutar")
            kat_toplamlari[kat] += self.set_res("fosseptik", "Fosseptik İşlemi", t_fos)
        else: kat_toplamlari[kat] += self.set_res("fosseptik", "Girdi Yok", 0)
        
        m3 = self.v("kirim_malzeme", "Kırılacak Hacim m3")
        if m3 > 0:
            c_carpan = self.v("kirim_malzeme", "[A]1 m3 Kaç Çuval (V:60)", 60)
            ton_carpan = self.v("kirim_malzeme", "[A]1 m3 Kaç Ton (V:1.5)", 1.5) # Yeni eklenen ton çarpanı
            ton = m3 * ton_carpan
            t = math.ceil(m3 * c_carpan) * self.v("kirim_malzeme", "[F]Çuval Atım Tutar")
            kat_toplamlari[kat] += self.set_res("kirim_malzeme", f"Moloz: {ton:.1f} Ton | {math.ceil(m3 * c_carpan)} Çuval", t)
        else: kat_toplamlari[kat] += self.set_res("kirim_malzeme", "Girdi Yok", 0)
        
        kaz_m2 = self.v("kazim_eks", "Alan m2")
        if kaz_m2 > 0:
            der = self.v("kazim_eks", "Derinlik m")
            zem = self.v("kazim_eks", "Zemin Tipi (1,2,3)")
            
            y_hiz = self.v("kazim_eks", "[A]Yumuşak m3/Saat(V:50)", 50)
            s_hiz = self.v("kazim_eks", "[A]Sert m3/Saat(V:20)", 20)
            k_hiz = self.v("kazim_eks", "[A]Kaya m3/Saat(V:10)", 10)
            
            # Girilen zemin tipine göre ilgili saatlik kazı hızını seç
            hiz_carpani = y_hiz if zem == 1 else (s_hiz if zem == 2 else k_hiz)
            
            saat = math.ceil((kaz_m2 * der) / hiz_carpani) if der > 0 and zem in [1, 2, 3] and hiz_carpani > 0 else 0
            t = saat * self.v("kazim_eks", "[F]Saatlik Tutar")
            kat_toplamlari[kat] += self.set_res("kazim_eks", f"Ekskavatör: {saat} Saat", t)
        else: kat_toplamlari[kat] += self.set_res("kazim_eks", "Girdi Yok", 0)
            
        t_kalip = self.v("kalip", "Alan m2") * self.v("kalip", "[F]m2 Tutar") if self.v("kalip", "Alan m2") > 0 else 0
        kat_toplamlari[kat] += self.set_res("kalip", "Kalıp İşlemi", t_kalip)

        tas_m3 = self.v("tas_duvar", "Hacim m3")
        if tas_m3 > 0:
            tas_cim = math.ceil(tas_m3 * self.v("tas_duvar", "[A]1m3 Taşa Çimnt(V:4)", 4))
            tas_kum = math.ceil(tas_m3 * self.v("tas_duvar", "[A]1m3 Taşa Kum(V:15)", 15))
            tas_kir = math.ceil(tas_m3 * self.v("tas_duvar", "[A]1m3 Taşa Kireç(V:1)", 1))
            t = (tas_m3 * self.v("tas_duvar", "[F]Taş m3 Tutar")) + (tas_cim * self.v("tas_duvar", "[F]Çimento(50kg) Tutar")) + (tas_kum * self.v("tas_duvar", "[F]Kum(Çuval) Tutar")) + (tas_kir * self.v("tas_duvar", "[F]Kireç(Torba) Tutar"))
            kat_toplamlari[kat] += self.set_res("tas_duvar", f"Çim: {tas_cim} T. | Kum: {tas_kum} Çuv. | Kir: {tas_kir} Torba", t)
        else: kat_toplamlari[kat] += self.set_res("tas_duvar", "Girdi Yok", 0)

        g5 = self.v("gazbeton", "5'lik Alan m2"); g10 = self.v("gazbeton", "10'luk Alan m2"); g20 = self.v("gazbeton", "20'lik Alan m2")
        if (g5 + g10 + g20) > 0:
            g_carpan = self.v("gazbeton", "[A]1m2 Gazbeton Adeti(V:7)", 7)
            t_carpan = self.v("gazbeton", "[A]1m2 Tutkal kg(V:4)", 4)
            
            # Adet Hesapları
            ad5 = math.ceil(g5 * g_carpan) if g5 > 0 else 0
            ad10 = math.ceil(g10 * g_carpan) if g10 > 0 else 0
            ad20 = math.ceil(g20 * g_carpan) if g20 > 0 else 0
            
            # Bireysel Tutkal Hesapları (Sadece bilgi amaçlı ekranda göstermek için)
            t5 = math.ceil((g5 * t_carpan) / 25) if g5 > 0 else 0
            t10 = math.ceil((g10 * t_carpan) / 25) if g10 > 0 else 0
            t20 = math.ceil((g20 * t_carpan) / 25) if g20 > 0 else 0
            
            # GERÇEK TUTKAL HESABI (Fiyatlandırma için toplam kg üzerinden tek yuvarlama yapılır)
            toplam_tutkal_kg = (g5 + g10 + g20) * t_carpan
            gercek_torba = math.ceil(toplam_tutkal_kg / 25)
            
            # Fiyat Çarpımı
            t_toplam = (ad5 * self.v("gazbeton", "[F]5'lik Adet Tutar")) + \
                       (ad10 * self.v("gazbeton", "[F]10'luk Adet Tutar")) + \
                       (ad20 * self.v("gazbeton", "[F]20'lik Adet Tutar")) + \
                       (gercek_torba * self.v("gazbeton", "[F]Örgü Tutkal(25kg) Tutar"))
            
            detay = []
            if g5 > 0: detay.append(f"5'lik:{ad5}Ad({t5}T)")
            if g10 > 0: detay.append(f"10'luk:{ad10}Ad({t10}T)")
            if g20 > 0: detay.append(f"20'lik:{ad20}Ad({t20}T)")
            
            # Sonuna da parayı ödediğin gerçek toplam torbayı yazdıralım
            sonuc_yazisi = " | ".join(detay) + f" = Top. {gercek_torba} Torba"
            
            kat_toplamlari[kat] += self.set_res("gazbeton", sonuc_yazisi, t_toplam)
        else: 
            kat_toplamlari[kat] += self.set_res("gazbeton", "Girdi Yok", 0)
            
        sap_m2 = self.v("sap", "Alan m2")
        if sap_m2 > 0:
            sap_tonaj = self.v("sap", "[A]1m3 Şap Tonaj(V:2000kg)", 2000)
            sap_torba = math.ceil((sap_m2 * (self.v("sap", "Kalınlık cm")/100) * sap_tonaj) / 25)
            t = sap_torba * self.v("sap", "[F]Hazır Şap(25kg) Tutar")
            kat_toplamlari[kat] += self.set_res("sap", f"Hazır Şap: {sap_torba} Torba", t)
        else: kat_toplamlari[kat] += self.set_res("sap", "Girdi Yok", 0)

        bs_m3 = self.v("beton_sap", "Hacim m3")
        if bs_m3 > 0:
            bs_cimen = math.ceil((bs_m3 * self.v("beton_sap", "[A]1m3 Şapa Çimnt(V:300kg)", 300)) / 50)
            bs_kum = math.ceil((bs_m3 * self.v("beton_sap", "[A]1m3 Şapa Kum(V:1500kg)", 1500)) / 25)
            t = (bs_cimen * self.v("beton_sap", "[F]Çimento(50kg) Tutar")) + (bs_kum * self.v("beton_sap", "[F]Kum(25kg) Tutar"))
            kat_toplamlari[kat] += self.set_res("beton_sap", f"Çimento: {bs_cimen} T. | Kum: {bs_kum} Ç.", t)
        else: kat_toplamlari[kat] += self.set_res("beton_sap", "Girdi Yok", 0)

        # 2. ALTYAPI
        kat = "2. ALTYAPI İŞLEMLERİ"
        oda = self.v("elektrik", "Oda Sayısı")
        if oda > 0:
            # Dinamik Çarpanlar
            c_priz = self.v("elektrik", "[A]Odabaşı Priz(V:3)", 3)
            c_sigorta = self.v("elektrik", "[A]Odabaşı Sig(V:1)", 1)
            c_kablo = self.v("elektrik", "[A]Odabaşı Kablo(V:0.5)", 0.5)
            
            # Otomatik Adet Hesapları
            toplam_priz = math.ceil(oda * c_priz)
            toplam_sigorta = math.ceil(oda * c_sigorta)
            toplam_kablo = math.ceil(oda * c_kablo)
            
            # Manuel Girilen Adetler
            aydinlatma_ad = self.v("elektrik", "Aydınlatma Adedi")
            aplik_ad = self.v("elektrik", "Aplik Adedi")
            anahtar_ad = self.v("elektrik", "Anahtar Adedi")
            internet_ad = self.v("elektrik", "İnternet Adedi")
            anten_ad = self.v("elektrik", "Anten Adedi")
            led_mt = self.v("elektrik", "Led mt")
            kedi_ad = self.v("elektrik", "Kedi Gözü Ad")
            
            # Tutar Çarpımları
            t_elek = (toplam_priz * self.v("elektrik", "[F]Priz Tutar")) + \
                     (toplam_sigorta * self.v("elektrik", "[F]Sigorta Tutar")) + \
                     (toplam_kablo * self.v("elektrik", "[F]Kablo(Top) Tutar")) + \
                     (aydinlatma_ad * self.v("elektrik", "[F]Aydınlatma Tutar")) + \
                     (aplik_ad * self.v("elektrik", "[F]Aplik Tutar")) + \
                     (anahtar_ad * self.v("elektrik", "[F]Anahtar Tutar")) + \
                     (internet_ad * self.v("elektrik", "[F]İnternet Tutar")) + \
                     (anten_ad * self.v("elektrik", "[F]Anten Tutar")) + \
                     (led_mt * self.v("elektrik", "[F]Led mt Tutar")) + \
                     (kedi_ad * self.v("elektrik", "[F]Kedi Gözü Tutar")) + \
                     self.v("elektrik", "[F]Ek Gider Toplam Tutar")
            
            # Çıktı Metni
            detay = f"Priz:{toplam_priz} | Sig:{toplam_sigorta} | Kablo:{toplam_kablo}Top | Anahtar:{anahtar_ad} | İnternet:{internet_ad} | Anten:{anten_ad} | Led:{led_mt}m"
            
            kat_toplamlari[kat] += self.set_res("elektrik", detay, t_elek)
        else: 
            kat_toplamlari[kat] += self.set_res("elektrik", "Girdi Yok", 0)

        su_m2 = self.v("su", "Alan m2")
        if su_m2 > 0:
            t_su = su_m2 * self.v("su", "[F]m2 Tutar")
            kat_toplamlari[kat] += self.set_res("su", f"Su Tesisatı: {su_m2} m2", t_su)
        else: 
            kat_toplamlari[kat] += self.set_res("su", "Girdi Yok", 0)
        
        dg_oda = self.v("dogalgaz", "Oda Sayısı")
        if dg_oda > 0:
            t = (self.v("dogalgaz", "Kombi Adedi") * self.v("dogalgaz", "[F]Kombi Tutar")) + (self.v("dogalgaz", "Petek mt") * self.v("dogalgaz", "[F]Petek mt Tutar")) + self.v("dogalgaz", "[F]Tesisat Toplam Tutar")
            kat_toplamlari[kat] += self.set_res("dogalgaz", "Doğalgaz Sistemi", t)
        else: kat_toplamlari[kat] += self.set_res("dogalgaz", "Girdi Yok", 0)

        term_ad = self.v("termosifon", "Adet")
        if term_ad > 0:
            t_term = term_ad * self.v("termosifon", "[F]Adet Tutar")
            kat_toplamlari[kat] += self.set_res("termosifon", f"Termosifon: {term_ad} Adet", t_term)
        else: 
            kat_toplamlari[kat] += self.set_res("termosifon", "Girdi Yok", 0)

        # 3. DOĞRAMALAR
        kat = "3. DOĞRAMALAR"
        p_win = self.v("pimapen", "Winner m2"); p_ege = self.v("pimapen", "Egepen m2"); p_win2 = self.v("pimapen", "Winsa m2"); p_alu = self.v("pimapen", "Alüminyum m2")
        if (p_win + p_ege + p_win2 + p_alu) > 0:
            t = (p_win*self.v("pimapen", "[F]Winner Tutar"))+(p_ege*self.v("pimapen", "[F]Egepen Tutar"))+(p_win2*self.v("pimapen", "[F]Winsa Tutar"))+(p_alu*self.v("pimapen", "[F]Alüminyum Tutar"))
            kat_toplamlari[kat] += self.set_res("pimapen", "Pencereler", t)
        else: kat_toplamlari[kat] += self.set_res("pimapen", "Girdi Yok", 0)
        
        l_ad = self.v("kapi", "Lake Ad")
        p_ad = self.v("kapi", "Panel Ad")
        m_ad = self.v("kapi", "Masif Ad")
        mel_ad = self.v("kapi", "Melamin Ad")
        pvc_ad = self.v("kapi", "PVC Ad")
        
        if (l_ad + p_ad + m_ad + mel_ad + pvc_ad) > 0:
            t_kapi = (l_ad * self.v("kapi", "[F]Lake Tutar")) + \
                     (p_ad * self.v("kapi", "[F]Panel Tutar")) + \
                     (m_ad * self.v("kapi", "[F]Masif Tutar")) + \
                     (mel_ad * self.v("kapi", "[F]Melamin Tutar")) + \
                     (pvc_ad * self.v("kapi", "[F]PVC Tutar"))
            
            detay = []
            if l_ad > 0: detay.append(f"Lake: {l_ad}Ad")
            if p_ad > 0: detay.append(f"Panel: {p_ad}Ad")
            if m_ad > 0: detay.append(f"Masif: {m_ad}Ad")
            if mel_ad > 0: detay.append(f"Melamin: {mel_ad}Ad")
            if pvc_ad > 0: detay.append(f"PVC: {pvc_ad}Ad")
            
            kat_toplamlari[kat] += self.set_res("kapi", " | ".join(detay), t_kapi)
        else:
            kat_toplamlari[kat] += self.set_res("kapi", "Girdi Yok", 0)

        v_ad = self.v("celik_kapi", "Villa Ad")
        d_ad = self.v("celik_kapi", "Daire Ad")
        b_ad = self.v("celik_kapi", "Bina Ad")
        
        if (v_ad + d_ad + b_ad) > 0:
            t_celik = (v_ad * self.v("celik_kapi", "[F]Villa Tutar")) + \
                      (d_ad * self.v("celik_kapi", "[F]Daire Tutar")) + \
                      (b_ad * self.v("celik_kapi", "[F]Bina Tutar"))
            
            detay = []
            if v_ad > 0: detay.append(f"Villa: {v_ad}Ad")
            if d_ad > 0: detay.append(f"Daire: {d_ad}Ad")
            if b_ad > 0: detay.append(f"Bina: {b_ad}Ad")
            
            kat_toplamlari[kat] += self.set_res("celik_kapi", " | ".join(detay), t_celik)
        else:
            kat_toplamlari[kat] += self.set_res("celik_kapi", "Girdi Yok", 0)

        o_ad = self.v("kepenk", "Otomatik Ad")
        m_ad = self.v("kepenk", "Manuel Ad")
        
        if (o_ad + m_ad) > 0:
            t_kepenk = (o_ad * self.v("kepenk", "[F]Oto. Tutar")) + \
                       (m_ad * self.v("kepenk", "[F]Man. Tutar"))
            
            detay = []
            if o_ad > 0: detay.append(f"Oto: {o_ad}Ad")
            if m_ad > 0: detay.append(f"Manuel: {m_ad}Ad")
            
            kat_toplamlari[kat] += self.set_res("kepenk", " | ".join(detay), t_kepenk)
        else:
            kat_toplamlari[kat] += self.set_res("kepenk", "Girdi Yok", 0)

        s_m2 = self.v("cambalkon", "Standart m2")
        k_m2 = self.v("cambalkon", "Konfor m2")
        j_m2 = self.v("cambalkon", "Jaluzi m2")
        
        if (s_m2 + k_m2 + j_m2) > 0:
            t_cam = (s_m2 * self.v("cambalkon", "[F]Std Tutar")) + \
                    (k_m2 * self.v("cambalkon", "[F]Konfor Tutar")) + \
                    (j_m2 * self.v("cambalkon", "[F]Jaluzi Tutar"))
            
            detay = []
            if s_m2 > 0: detay.append(f"Std: {s_m2}m2")
            if k_m2 > 0: detay.append(f"Konfor: {k_m2}m2")
            if j_m2 > 0: detay.append(f"Jaluzi: {j_m2}m2")
            
            kat_toplamlari[kat] += self.set_res("cambalkon", " | ".join(detay), t_cam)
        else:
            kat_toplamlari[kat] += self.set_res("cambalkon", "Girdi Yok", 0)

        menfez_ad = self.v("menfez", "Adet")
        if menfez_ad > 0:
            t_menfez = menfez_ad * self.v("menfez", "[F]Adet Tutar")
            kat_toplamlari[kat] += self.set_res("menfez", f"Menfez: {menfez_ad} Adet", t_menfez)
        else:
            kat_toplamlari[kat] += self.set_res("menfez", "Girdi Yok", 0)
            
        # 4. KAPLAMALAR    
        kat = "4. KAPLAMALAR"
        # PARKE HESABI
        lam_m2 = self.v("parke", "Laminant Alan m2")
        lne_m2 = self.v("parke", "Lamine Alan m2")
        mas_m2 = self.v("parke", "Masif Alan m2")
        sup_mt = self.v("parke", "Süpürgelik mt")
        sil_m2 = self.v("parke", "Şilte m2")
        
        if (lam_m2 + lne_m2 + mas_m2 + sup_mt + sil_m2) > 0:
            # Paket/Boy/Rulo Hesapları (Yukarı yuvarlanarak)
            lam_pkt = math.ceil(lam_m2 / self.v("parke", "[A]Laminant Paket m2", 1.8)) if lam_m2 > 0 else 0
            lne_pkt = math.ceil(lne_m2 / self.v("parke", "[A]Lamine Paket m2", 1.8)) if lne_m2 > 0 else 0
            mas_pkt = math.ceil(mas_m2 / self.v("parke", "[A]Masif Paket m2", 1.8)) if mas_m2 > 0 else 0
            
            sup_boy = math.ceil(sup_mt / self.v("parke", "[A]Süp. Boyu(V:2.8m)", 2.8)) if sup_mt > 0 else 0
            silte_rulo = math.ceil(sil_m2 / self.v("parke", "[A]Şilte Rulo(V:15m2)", 15)) if sil_m2 > 0 else 0
            
            # Fiyat Çarpımları
            t_parke = (lam_pkt * self.v("parke", "[F]Lam.Paket Tutar")) + \
                      (lne_pkt * self.v("parke", "[F]Lamine Pkt Tutar")) + \
                      (mas_pkt * self.v("parke", "[F]Masif Pkt Tutar")) + \
                      (sup_mt * self.v("parke", "[F]Süpürgelik mt Tutar")) + \
                      (sil_m2 * self.v("parke", "[F]Şilte m2 Tutar"))
                      
            # Sadece veri girilenleri ekrana yazdırma
            detay = []
            if lam_pkt > 0: detay.append(f"Lmnt: {lam_pkt}Pkt")
            if lne_pkt > 0: detay.append(f"Lam: {lne_pkt}Pkt")
            if mas_pkt > 0: detay.append(f"Masif: {mas_pkt}Pkt")
            if sup_boy > 0: detay.append(f"Süpürgelik: {sup_boy}Boy")
            if silte_rulo > 0: detay.append(f"Şilte: {silte_rulo}Rulo")
            
            kat_toplamlari[kat] += self.set_res("parke", " | ".join(detay), t_parke)
        else:
            kat_toplamlari[kat] += self.set_res("parke", "Girdi Yok", 0)

        # FAYANS HESABI
        f_m2 = self.v("fayans", "Toplam Alan m2")
        if f_m2 > 0:
            f_en = self.v("fayans", "Fayans En cm")
            f_boy = self.v("fayans", "Fayans Boy cm")
            
            # Adet Hesabı (Eğer En ve Boy girildiyse)
            f_adet = 0
            if f_en > 0 and f_boy > 0:
                tek_fayans_m2 = (f_en * f_boy) / 10000
                f_adet = math.ceil(f_m2 / tek_fayans_m2)
            
            # Sarfiyat Hesapları (Matematik konuşsun!)
            kalekim_kg = f_m2 * self.v("fayans", "[A]1m2 Kalekim kg(V:6)", 6)
            kal_torba = math.ceil(kalekim_kg / 25) # 25kg'lık torbalar
            derz_torba = math.ceil((f_m2 * 0.5) / 5) # m2'ye ortalama 0.5kg derz (5kg torba)
            arti_paket = math.ceil(f_m2 / 20) # Ortalama 20m2'ye 1 paket derz artısı
            
            # Fiyat Çarpımları
            t_fayans = (f_m2 * self.v("fayans", "[F]m2 Tutar")) + \
                       (kal_torba * self.v("fayans", "[F]Kalekim(25kg) Tutar")) + \
                       (derz_torba * self.v("fayans", "[F]Derz(5kg) Tutar")) + \
                       (arti_paket * self.v("fayans", "[F]Derz Artısı(Pk) Tutar"))
                       
            # Ekrana Şık Döküm Yazdırma
            adet_metni = f"({f_adet} Adet)" if f_adet > 0 else ""
            detay = f"Fayans: {f_m2}m2 {adet_metni} | Klkm: {kal_torba}T | Derz: {derz_torba}T | Artı: {arti_paket}Pk"
            
            kat_toplamlari[kat] += self.set_res("fayans", detay, t_fayans)
        else:
            kat_toplamlari[kat] += self.set_res("fayans", "Girdi Yok", 0)

        # 5. İNCE İŞÇİLİK
        kat = "5. İNCE İŞÇİLİK"
        ds_m2 = self.v("duvar_siva", "Alan m2")
        if ds_m2 > 0:
            ds_alci = math.ceil((ds_m2 * self.v("duvar_siva", "[A]1 Torba Alçı m2(V:3)", 3)) / 25)
            ds_file = math.ceil(ds_m2 / self.v("duvar_siva", "[A]1 Top File mt(V:50)", 50))
            t = (ds_alci * self.v("duvar_siva", "[F]Alçı Torba Tutar")) + (ds_file * self.v("duvar_siva", "[F]File(Top) Tutar"))
            kat_toplamlari[kat] += self.set_res("duvar_siva", f"Alçı: {ds_alci} Torba | File: {ds_file} Top", t)
        else: kat_toplamlari[kat] += self.set_res("duvar_siva", "Girdi Yok", 0)

        # TAVAN SIVA HESABI
        t_alan = self.v("tavan_siva", "Alan m2")
        if t_alan > 0:
            alci_carpan = self.v("tavan_siva", "[A]1 Torba Alçı m2(V:3)", 3)
            file_carpan = self.v("tavan_siva", "[A]1 Top File mt(V:50)", 50)
            
            torba = math.ceil(t_alan / alci_carpan) if alci_carpan > 0 else 0
            file_top = math.ceil(t_alan / file_carpan) if file_carpan > 0 else 0
            
            t_tavan = (torba * self.v("tavan_siva", "[F]Alçı Torba Tutar")) + \
                      (file_top * self.v("tavan_siva", "[F]File(Top) Tutar"))
            
            detay = f"Tavan: {t_alan}m2 | Alçı: {torba} Torba | File: {file_top} Top"
            
            kat_toplamlari[kat] += self.set_res("tavan_siva", detay, t_tavan)
        else:
            kat_toplamlari[kat] += self.set_res("tavan_siva", "Girdi Yok", 0)

        # ASMA TAVAN HESABI
        a_m2 = self.v("asma_tavan", "Alan m2")
        if a_m2 > 0:
            # God Mode Çarpanları
            plk_m2 = self.v("asma_tavan", "[A]1 Plk Alçıpan m2(V:3)", 3)
            u_boy = self.v("asma_tavan", "[A]1m2 U-Profil Boy(V:0.3)", 0.3)
            c_boy = self.v("asma_tavan", "[A]1m2 C-Profil Boy(V:0.8)", 0.8)
            bant_m2 = self.v("asma_tavan", "[A]1 Top Bant m2(V:50)", 50)
            alci_m2 = self.v("asma_tavan", "[A]1 Torba Alçı m2(V:10)", 10)
            vida_m2 = self.v("asma_tavan", "[A]1 Pkt Vida m2(V:25)", 25)

            # Adet/Kutu/Paket Hesapları
            plk_ad = math.ceil(a_m2 / plk_m2) if plk_m2 > 0 else 0
            u_ad = math.ceil(a_m2 * u_boy)
            c_ad = math.ceil(a_m2 * c_boy)
            bant_ad = math.ceil(a_m2 / bant_m2) if bant_m2 > 0 else 0
            alci_ad = math.ceil(a_m2 / alci_m2) if alci_m2 > 0 else 0
            vida_ad = math.ceil(a_m2 / vida_m2) if vida_m2 > 0 else 0

            # Fiyat Çarpımları
            t_asma = (plk_ad * self.v("asma_tavan", "[F]Alçıpan Plk Tutar")) + \
                     (u_ad * self.v("asma_tavan", "[F]U-Profil Tutar")) + \
                     (c_ad * self.v("asma_tavan", "[F]C-Profil Tutar")) + \
                     (bant_ad * self.v("asma_tavan", "[F]Derz Bandı Tutar")) + \
                     (alci_ad * self.v("asma_tavan", "[F]Sıva/Alçı Torba Tutar")) + \
                     (vida_ad * self.v("asma_tavan", "[F]Vida/Dübel Tutar"))

            # Ekrana Yazdırılacak Döküm
            detay = f"Alçıpan:{plk_ad}Plk | U:{u_ad}Boy | C:{c_ad}Boy | Bant:{bant_ad}Tp | Alçı:{alci_ad}T | Vida:{vida_ad}Pkt"

            kat_toplamlari[kat] += self.set_res("asma_tavan", detay, t_asma)
        else:
            kat_toplamlari[kat] += self.set_res("asma_tavan", "Girdi Yok", 0)

        # KLİPİN TAVAN HESABI
        k_alan = self.v("klipin", "Alan m2")
        if k_alan > 0:
            # 30x30 plaka = 0.09 m2
            plaka_adet = math.ceil(k_alan / 0.09)
            led_adet = self.v("klipin", "Kare Led Adedi")
            
            # Fiyat Çarpımları (Plaka ve Led adetle, diğerleri m2 ile çarpılır)
            t_klipin = (plaka_adet * self.v("klipin", "[F]Plaka Adet Tutar")) + \
                       (k_alan * self.v("klipin", "[F]U-C Profil Tutar")) + \
                       (k_alan * self.v("klipin", "[F]Askı/Yay Tutar")) + \
                       (k_alan * self.v("klipin", "[F]Vida/Dübel Tutar")) + \
                       (led_adet * self.v("klipin", "[F]Kare Led Tutar"))
            
            detay = f"Klipin: {k_alan}m2 ({plaka_adet} Plaka) | Kare Led: {led_adet} Adet"
            
            kat_toplamlari[kat] += self.set_res("klipin", detay, t_klipin)
        else:
            kat_toplamlari[kat] += self.set_res("klipin", "Girdi Yok", 0)

        # KÖŞE STRAFORU (STROPİYER) HESABI
        s_m2 = self.v("stropiyer", "Toplam Tavan m2")
        if s_m2 > 0:
            fire = self.v("stropiyer", "[A]Stropiyer Fire(V:1.1)", 1.1)
            
            # m2'den tahmini çevre (mt) bulma (Kare oda varsayımı)
            cevre_mt = math.sqrt(s_m2) * 4
            toplam_mt = math.ceil(cevre_mt * fire)
            
            t_stropiyer = toplam_mt * self.v("stropiyer", "[F]Strafor mt Tutar")
            
            detay = f"Stropiyer: ~{toplam_mt}mt (Tahmini Çevre + Fire)"
            
            kat_toplamlari[kat] += self.set_res("stropiyer", detay, t_stropiyer)
        else:
            kat_toplamlari[kat] += self.set_res("stropiyer", "Girdi Yok", 0)

        # MANTOLAMA HESABI
        m_alan = self.v("mantolama", "Alan m2")
        if m_alan > 0:
            secim = self.v("mantolama", "Yalıtım(1:EPS 2:XPS 3:Taş)", 1)
            
            # God Mode Çarpanları
            yapi_kg = self.v("mantolama", "[A]Yapıştırıcı kg/m2(V:5)", 5)
            siva_kg = self.v("mantolama", "[A]Sıva kg/m2(V:5)", 5)
            file_carp = self.v("mantolama", "[A]File Çarpan(V:1.1)", 1.1)
            dubel_ad = self.v("mantolama", "[A]Dübel Ad/m2(V:6)", 6)
            dek_kg = self.v("mantolama", "[A]Dek.Sıva kg/m2(V:3)", 3)
            
            # Sarfiyat Hesapları (Matematik konuşsun)
            yapi_torba = math.ceil((m_alan * yapi_kg) / 25)
            siva_torba = math.ceil((m_alan * siva_kg) / 25)
            file_top = math.ceil((m_alan * file_carp) / 50) # 1 Top File genelde 50m2'dir
            toplam_dubel = math.ceil(m_alan * dubel_ad)
            dek_torba = math.ceil((m_alan * dek_kg) / 25)
            
            # Yalıtım Malzemesi Akıllı Fiyat Seçimi
            yalitim_maliyet = 0
            yalitim_isim = "EPS"
            if secim == 1:
                yalitim_maliyet = m_alan * self.v("mantolama", "[F]EPS m2 Tutar")
                yalitim_isim = "EPS"
            elif secim == 2:
                yalitim_maliyet = m_alan * self.v("mantolama", "[F]XPS m2 Tutar")
                yalitim_isim = "XPS"
            elif secim == 3:
                yalitim_maliyet = m_alan * self.v("mantolama", "[F]Taşyünü m2 Tutar")
                yalitim_isim = "Taşyünü"
            else:
                yalitim_isim = "Hatalı Seçim!"
                
            # Toplam Maliyet Çarpımı
            t_manto = yalitim_maliyet + \
                      (yapi_torba * self.v("mantolama", "[F]Yapıştırıcı(25kg) Tutar")) + \
                      (siva_torba * self.v("mantolama", "[F]Sıva(25kg) Tutar")) + \
                      (file_top * self.v("mantolama", "[F]File(Top) Tutar")) + \
                      (toplam_dubel * self.v("mantolama", "[F]Dübel Adet Tutar")) + \
                      (dek_torba * self.v("mantolama", "[F]Dek.Sıva(25kg) Tutar"))
                      
            # Ekrana Yazdırılacak Profesyonel Döküm
            detay = f"{yalitim_isim}: {m_alan}m2 | Ypş: {yapi_torba}T | Sıva: {siva_torba}T | File: {file_top}Tp | Dübel: {toplam_dubel}Ad | Dek: {dek_torba}T"
            
            kat_toplamlari[kat] += self.set_res("mantolama", detay, t_manto)
        else:
            kat_toplamlari[kat] += self.set_res("mantolama", "Girdi Yok", 0)

        # İÇ CEPHE BOYA HESABI
        ic_alan = self.v("ic_boya", "Alan m2")
        if ic_alan > 0:
            boya_carpan = self.v("ic_boya", "[A]1m2 Boya Lt(V:0.3)", 0.3)
            astar_carpan = self.v("ic_boya", "[A]1m2 Astar Lt(V:0.1)", 0.1)
            
            # Kova Hesapları (Boya 20L, Astar 10L kabul edilmiştir)
            boya_kova = math.ceil((ic_alan * boya_carpan) / 20)
            astar_kova = math.ceil((ic_alan * astar_carpan) / 10)
            rulo_ad = self.v("ic_boya", "Rulo/Fırça Ad")
            
            t_ic = (boya_kova * self.v("ic_boya", "[F]Boya 20L Tutar")) + \
                   (astar_kova * self.v("ic_boya", "[F]Astar 10L Tutar")) + \
                   (rulo_ad * self.v("ic_boya", "[F]Sarf Ad Tutar"))
                   
            detay = f"İç Boya: {ic_alan}m2 | Boya(20L): {boya_kova} Kova | Astar(10L): {astar_kova} Kova | Rulo/Sarf: {rulo_ad} Ad"
            kat_toplamlari[kat] += self.set_res("ic_boya", detay, t_ic)
        else:
            kat_toplamlari[kat] += self.set_res("ic_boya", "Girdi Yok", 0)

        # DIŞ CEPHE BOYA HESABI
        dis_alan = self.v("dis_boya", "Alan m2")
        if dis_alan > 0:
            d_boya_carpan = self.v("dis_boya", "[A]1m2 Boya Lt(V:0.3)", 0.3)
            d_astar_carpan = self.v("dis_boya", "[A]1m2 Astar Lt(V:0.1)", 0.1)
            
            # Kova Hesapları (Boya 20L, Astar 10L kabul edilmiştir)
            d_boya_kova = math.ceil((dis_alan * d_boya_carpan) / 20)
            d_astar_kova = math.ceil((dis_alan * d_astar_carpan) / 10)
            d_rulo_ad = self.v("dis_boya", "Rulo/Fırça Ad")
            
            t_dis = (d_boya_kova * self.v("dis_boya", "[F]Boya 20L Tutar")) + \
                    (d_astar_kova * self.v("dis_boya", "[F]Astar 10L Tutar")) + \
                    (d_rulo_ad * self.v("dis_boya", "[F]Sarf Ad Tutar"))
                   
            detay_dis = f"Dış Boya: {dis_alan}m2 | Boya(20L): {d_boya_kova} Kova | Astar(10L): {d_astar_kova} Kova | Rulo/Sarf: {d_rulo_ad} Ad"
            kat_toplamlari[kat] += self.set_res("dis_boya", detay_dis, t_dis)
        else:
            kat_toplamlari[kat] += self.set_res("dis_boya", "Girdi Yok", 0)

        # 6. BANYO AKSESUARLARI
        kat = "6. BANYO AKSESUARLARI"
        b_evye = self.v("b_aksesuar", "Evye Ad")
        if b_evye > 0:
            t = (b_evye*self.v("b_aksesuar", "[F]Evye Tutar"))+(self.v("b_aksesuar", "Batarya Ad")*self.v("b_aksesuar", "[F]Batarya Tutar"))+(self.v("b_aksesuar", "D.Başlık Ad")*self.v("b_aksesuar", "[F]D.Başlık Tutar"))+(self.v("b_aksesuar", "D.Batarya Ad")*self.v("b_aksesuar", "[F]D.Batarya Tutar"))
            kat_toplamlari[kat] += self.set_res("b_aksesuar", "Vitrifiye / Armatür", t)
        else: kat_toplamlari[kat] += self.set_res("b_aksesuar", "Girdi Yok", 0)

        # KLOZETLER HESABI
        gomme = self.v("klozet", "Gömme Ad")
        duv = self.v("klozet", "Duv.Sıfır Ad")
        klasik = self.v("klozet", "Klasik Ad")
        alaturka = self.v("klozet", "Alaturka Ad")
        
        if (gomme + duv + klasik + alaturka) > 0:
            t_klozet = (gomme * self.v("klozet", "[F]Gömme Tutar")) + \
                       (duv * self.v("klozet", "[F]Duv.Sıfır Tutar")) + \
                       (klasik * self.v("klozet", "[F]Klasik Tutar")) + \
                       (alaturka * self.v("klozet", "[F]Alaturka Tutar"))
                       
            detay_klozet = []
            if gomme > 0: detay_klozet.append(f"Gömme: {gomme}Ad")
            if duv > 0: detay_klozet.append(f"Duv.Sıfır: {duv}Ad")
            if klasik > 0: detay_klozet.append(f"Klasik: {klasik}Ad")
            if alaturka > 0: detay_klozet.append(f"Alaturka: {alaturka}Ad")
            
            kat_toplamlari[kat] += self.set_res("klozet", " | ".join(detay_klozet), t_klozet)
        else:
            kat_toplamlari[kat] += self.set_res("klozet", "Girdi Yok", 0)

        # DUŞAKABİN HESABI
        dusa_ad = self.v("dusakabin", "Adet")
        if dusa_ad > 0:
            t_dusa = dusa_ad * self.v("dusakabin", "[F]Adet Tutar")
            kat_toplamlari[kat] += self.set_res("dusakabin", f"Duşakabin: {dusa_ad} Adet", t_dusa)
        else:
            kat_toplamlari[kat] += self.set_res("dusakabin", "Girdi Yok", 0)

        # ==========================================
        kat = "7. MOBİLYA İMALATI"
        kat_toplamlari[kat] = 0

        # 1. BİLGİLENDİRME EKRANI (Ölçüye göre plaka tahmini)
        g_m2 = self.v("m_olcu", "Gövde Alan m2")
        k_m2 = self.v("m_olcu", "Kapak Alan m2")
        
        if (g_m2 + k_m2) > 0:
            g_carpan = self.v("m_olcu", "[A]Gövde Çarpanı(V:2)", 2.0)
            k_carpan = self.v("m_olcu", "[A]Kapak Çarpanı(V:1.2)", 1.2)
            s_mdf_plk = self.v("m_olcu", "[A]Sun/MDF Plk(V:5.88)", 5.88)
            hg_akr_plk = self.v("m_olcu", "[A]HG/Akr Plk(V:3.41)", 3.41)

            # USTANIN FORMÜLÜ
            g_sun = math.ceil(math.ceil(g_m2 / s_mdf_plk) * g_carpan) if s_mdf_plk > 0 else 0
            g_hg = math.ceil(math.ceil(g_m2 / hg_akr_plk) * g_carpan) if hg_akr_plk > 0 else 0
            
            k_sun = math.ceil(math.ceil(k_m2 / s_mdf_plk) * k_carpan) if s_mdf_plk > 0 else 0
            k_hg = math.ceil(math.ceil(k_m2 / hg_akr_plk) * k_carpan) if hg_akr_plk > 0 else 0
            
            # Tek satıra sığdırdık ki arayüzde taşma yapmasın!
            bilgi = f"Gövde: {g_sun} Sun/MDF veya {g_hg} Özel  |  Kapak: {k_sun} Sun/MDF veya {k_hg} Özel"
            
            kat_toplamlari[kat] += self.set_res("m_olcu", bilgi, 0)
        else:
            kat_toplamlari[kat] += self.set_res("m_olcu", "Girdi Yok", 0)

        # 2. PLAKA MALİYETLERİ
        plakalar = [("m_sun", "Suntalam"), ("m_mdf", "MDFlam"), ("m_hg", "HighGloss"), ("m_akr", "Akrilik"), ("m_lak", "Lake")]
        for p_id, p_isim in plakalar:
            p_ad = self.v(p_id, "Kullanılacak Plaka Ad")
            if p_ad > 0:
                p_tutar = p_ad * self.v(p_id, "[F]Plaka Tutar")
                kat_toplamlari[kat] += self.set_res(p_id, f"{p_isim}: {p_ad} Plaka", p_tutar)
            else:
                kat_toplamlari[kat] += self.set_res(p_id, "Girdi Yok", 0)

        # 3. İŞÇİLİK VE AKSESUARLAR
        aks_degerler = [
            ("Kesim", "Kesilecek Plaka Ad", "[F]Kesim(Plk) Tutar"), ("Bant", "Bantlama mt", "[F]Bantlama mt Tutar"),
            ("Menteşe", "Menteşe Ad", "[F]Menteşe Ad Tutar"), ("Ray", "Ray Ad", "[F]Ray Ad Tutar"),
            ("Kulp", "Kulp Ad", "[F]Kulp Ad Tutar"), ("Vida", "Vida Kutu", "[F]Vida Kutu Tutar"),
            ("Sürgü", "Sürgü Sistem Ad", "[F]Sürgü Ad Tutar"), ("Amortisör", "Amortisör Takım", "[F]Amortisör Tk Tutar"),
            ("Ayna", "Ayna mt", "[F]Ayna mt Tutar")
        ]
        t_aks = 0
        aks_detay = []
        for isim, g1, g2 in aks_degerler:
            mktr = self.v("m_aksesuar", g1)
            if mktr > 0:
                t_aks += mktr * self.v("m_aksesuar", g2)
                aks_detay.append(f"{isim}: {mktr}")
        
        if t_aks > 0:
            kat_toplamlari[kat] += self.set_res("m_aksesuar", " | ".join(aks_detay), t_aks)
        else:
            kat_toplamlari[kat] += self.set_res("m_aksesuar", "Girdi Yok", 0)

        # 4. TEZGAH VE EVYE
        tezgah_isimler = [("Çimstone mt", "[F]Çim.Tutar", "Çimstone"), ("Porselen mt", "[F]Por.Tutar", "Porselen"), ("Granit mt", "[F]Gra.Tutar", "Granit"), ("Corian mt", "[F]Cor.Tutar", "Corian"), ("Masif mt", "[F]Mas.Tutar", "Masif"), ("Mermer mt", "[F]Mer.Tutar", "Mermer")]
        t_tezgah = 0
        tezgah_detay = []
        for m_girdi, f_girdi, isim in tezgah_isimler:
            mt = self.v("m_tez", m_girdi)
            if mt > 0:
                t_tezgah += mt * self.v("m_tez", f_girdi)
                tezgah_detay.append(f"{isim}: {mt}mt")
        if t_tezgah > 0:
            kat_toplamlari[kat] += self.set_res("m_tez", " | ".join(tezgah_detay), t_tezgah)
        else:
            kat_toplamlari[kat] += self.set_res("m_tez", "Girdi Yok", 0)

        evye_isimler = [("Krom Evye Ad", "[F]Krom Tutar", "Krom"), ("Granit Evye Ad", "[F]Granit Tutar", "Granit"), ("Seramik Evye Ad", "[F]Ser. Tutar", "Seramik"), ("Batarya Ad", "[F]Batarya Tutar", "Batarya")]
        t_evye = 0
        evye_detay = []
        for m_girdi, f_girdi, isim in evye_isimler:
            ad = self.v("m_evy", m_girdi)
            if ad > 0:
                t_evye += ad * self.v("m_evy", f_girdi)
                evye_detay.append(f"{isim}: {ad}Ad")
        if t_evye > 0:
            kat_toplamlari[kat] += self.set_res("m_evy", " | ".join(evye_detay), t_evye)
        else:
            kat_toplamlari[kat] += self.set_res("m_evy", "Girdi Yok", 0)

        # ==========================================
        kat = "8. KARKAS & ÇATI"
        kat_toplamlari[kat] = 0

        # KARKAS HESABI (USTA İŞİ)
        alan_m2 = self.v("karkas", "Toplam Alan m2")
        uzunluk = self.v("karkas", "Duvar Toplam Uzunluk m")
        yukseklik = self.v("karkas", "Yükseklik m")
        
        if (uzunluk > 0 and yukseklik > 0) or alan_m2 > 0:
            bolucu = self.v("karkas", "Bölücü Duvar Ad")
            kapi = self.v("karkas", "Kapı Ad")
            pencere = self.v("karkas", "Pencere Ad")
            
            # Ustanın God Mode Çarpanları
            ana_aralik = self.v("karkas", "[A]Ana Dikme Ara(V:3m)", 3.0)
            ara_adet = self.v("karkas", "[A]Ara Dikme Adet(V:5)", 5.0)
            yatay_sira = self.v("karkas", "[A]Yatay Sıra(V:3)", 3.0)
            kapi_boy = self.v("karkas", "[A]Kapı Fire(V:1Boy)", 1.0)
            penc_boy = self.v("karkas", "[A]Penc. Fire(V:2Boy)", 2.0)
            tavan_carpan = self.v("karkas", "[A]Tavan Boy/m2(V:0.5)", 0.5)
            
            # --- 100x100 ANA TAŞIYICI (DİKME + ÜST HATIL) HESABI ---
            # 1. Ana Dikmeler: Uzunluk / 3m aralık + başlangıç direği
            ana_dikme_sayisi = math.ceil(uzunluk / ana_aralik) + 1 if ana_aralik > 0 else 0
            # 2. Bölücü duvar köşelerine çiftli destek
            bolucu_ana_sayisi = bolucu * 2
            
            toplam_dikey_100_mt = (ana_dikme_sayisi + bolucu_ana_sayisi) * yukseklik
            # 3. Üst Hatıl: Bütün sistemi üstten bağlayan yatay 100x100
            toplam_yatay_100_mt = uzunluk
            
            boy_100 = math.ceil((toplam_dikey_100_mt + toplam_yatay_100_mt) / 6)
            
            # --- 50x100 ARA TAŞIYICI VE TAVAN HESABI ---
            # 1. Ara Dikmeler: Her ana aralığa 5 adet ara dikme
            aralik_sayisi = math.ceil(uzunluk / ana_aralik) if ana_aralik > 0 else 0
            toplam_ara_dikme_sayisi = aralik_sayisi * ara_adet
            ara_dikey_mt = toplam_ara_dikme_sayisi * yukseklik
            
            # 2. Yatay Kayıtlar: Uzunluk boyunca atılacak kuşaklar
            ara_yatay_mt = uzunluk * yatay_sira
            
            # Dikey ve Yatayları toplayıp 6 metreye böl (Net Boy)
            boy_50_temel = math.ceil((ara_dikey_mt + ara_yatay_mt) / 6)
            
            # 3. Kapı ve Pencere Kör Kasa Boyları (Direkt Boy olarak eklenir)
            kapi_ekstra_boy = math.ceil(kapi * kapi_boy)
            penc_ekstra_boy = math.ceil(pencere * penc_boy)
            
            # 4. Tavan Izgarası (Alan üzerinden 50 cm aralıklarla)
            tavan_boy = math.ceil(alan_m2 * tavan_carpan)
            
            # 50x100 Genel Toplam
            boy_50 = boy_50_temel + kapi_ekstra_boy + penc_ekstra_boy + tavan_boy
            
            # Fiyat Çarpımları
            t_karkas = (boy_100 * self.v("karkas", "[F]100x100 Boy(6m) Tutar")) + \
                       (boy_50 * self.v("karkas", "[F]50x100 Boy(6m) Tutar")) + \
                       self.v("karkas", "[F]Kaynak/Sarf Tutar")
                       
            detay_karkas = f"100x100(Ana): {boy_100} Boy | 50x100(Ara+Tavan): {boy_50} Boy"
            kat_toplamlari[kat] += self.set_res("karkas", detay_karkas, t_karkas)
        else:
            kat_toplamlari[kat] += self.set_res("karkas", "Girdi Yok", 0)

        # ÇATI SİSTEMİ HESABI
        c_m2 = self.v("cati", "Alan m2")
        if c_m2 > 0:
            # God Mode Çarpanları
            makas_mt = self.v("cati", "[A]Makas mt/m2(V:1.2)", 1.2)
            asik_mt = self.v("cati", "[A]Aşık mt/m2(V:2.0)", 2.0)
            osb_m2 = self.v("cati", "[A]1 OSB m2(V:2.98)", 2.98)
            membran_m2 = self.v("cati", "[A]1 Rulo Membran m2(V:10)", 10)
            vida_m2 = self.v("cati", "[A]1 Kutu Vida m2(V:25)", 25)

            # Lojistik Adet/Boy/Rulo Hesapları (6 metre standart boy profil hesabıdır)
            makas_boy = math.ceil((c_m2 * makas_mt) / 6)
            asik_boy = math.ceil((c_m2 * asik_mt) / 6)
            osb_plk = math.ceil(c_m2 / osb_m2) if osb_m2 > 0 else 0
            membran_rulo = math.ceil(c_m2 / membran_m2) if membran_m2 > 0 else 0
            vida_kutu = math.ceil(c_m2 / vida_m2) if vida_m2 > 0 else 0
            
            # Fiyat Çarpımları
            t_cati = (makas_boy * self.v("cati", "[F]40x60 Makas Boy(6m) Tutar")) + \
                     (asik_boy * self.v("cati", "[F]40x40 Aşık Boy(6m) Tutar")) + \
                     (c_m2 * self.v("cati", "[F]Sandviç Pnl m2 Tutar")) + \
                     (osb_plk * self.v("cati", "[F]OSB Plaka Tutar")) + \
                     (membran_rulo * self.v("cati", "[F]Membran Rulo Tutar")) + \
                     (vida_kutu * self.v("cati", "[F]Akıllı Vida Tutar"))
                     
            detay = f"Çatı: {c_m2}m2 | Makas: {makas_boy} Boy | Aşık: {asik_boy} Boy | OSB: {osb_plk} Plk | Membran: {membran_rulo} Rulo | Vida: {vida_kutu} Kutu"
            
            kat_toplamlari[kat] += self.set_res("cati", detay, t_cati)
        else:
            kat_toplamlari[kat] += self.set_res("cati", "Girdi Yok", 0)

        # 9. ŞAHSİ GİDERLER
        kat = "9. ŞAHSİ GİDERLER"
        t = self.v("fatura", "Ay") * self.v("fatura", "[F]Aylık Tutar") if self.v("fatura", "Ay") > 0 else 0; kat_toplamlari[kat] += self.set_res("fatura", "Fatura", t)
        t = self.v("reklam", "Ay") * self.v("reklam", "[F]Aylık Tutar") if self.v("reklam", "Ay") > 0 else 0; kat_toplamlari[kat] += self.set_res("reklam", "Reklam", t)
        t = self.v("yol", "Gün") * self.v("yol", "[F]Günlük Tutar") if self.v("yol", "Gün") > 0 else 0; kat_toplamlari[kat] += self.set_res("yol", "Yol", t)
        t = self.v("yemek", "Gün") * self.v("yemek", "[F]Günlük Tutar") if self.v("yemek", "Gün") > 0 else 0; kat_toplamlari[kat] += self.set_res("yemek", "Yemek", t)


        # ==========================================
        kat = "10. GENEL İŞÇİLİK & TAŞERON"
        kat_toplamlari[kat] = 0

        # Tüm işçilik kalemlerini otomatik dönüp Birim x Tutar yapar
        for kalem in self.kategoriler[kat]:
            k_id = kalem["id"]
            k_baslik = kalem["baslik"]
            birim = self.v(k_id, "Birim")
            
            if birim > 0:
                tutar = birim * self.v(k_id, "[F]Tutar")
                kat_toplamlari[kat] += self.set_res(k_id, f"{k_baslik}: {birim} Birim", tutar)
            else:
                kat_toplamlari[kat] += self.set_res(k_id, "Girdi Yok", 0)

        # --- MALZEME VE İŞÇİLİK AYRIMI ---
        toplam_iscilik = 0.0
        toplam_malzeme = 0.0
        
        for k_adi, toplam in kat_toplamlari.items():
            self.kategori_toplam_etiketleri[k_adi].text = f"KATEGORİ TOPLAMI: {toplam:,.2f} TL"
            # 10. Kategori İşçiliktir, diğerleri Malzemedir.
            if "10." in k_adi:
                toplam_iscilik += toplam
            else:
                toplam_malzeme += toplam

        # --- KDV HESABI (Kâr zaten kalemlerin içine eklendi, burada sadece KDV kaldı) ---
        ekran = self.root.ids
        try:
            kdv_orani = float(ekran.kdv_orani.text.replace(',', '.')) if ekran.kdv_orani.text else 0.0
        except:
            kdv_orani = 0.0

        kdv_tutari = (toplam_malzeme + toplam_iscilik) * (kdv_orani / 100.0)
        net_genel_toplam = toplam_malzeme + toplam_iscilik + kdv_tutari

        # --- EKRANA TERTEMİZ YAZDIR ---
        ekran.lbl_malzeme.text = f"{toplam_malzeme:,.2f} TL"
        ekran.lbl_iscilik.text = f"{toplam_iscilik:,.2f} TL"
        ekran.lbl_kdv.text = f"{kdv_tutari:,.2f} TL"
        ekran.genel_toplam.text = f"{net_genel_toplam:,.2f} TL"
        
if __name__ == "__main__":
    MasterHesapApp().run()
