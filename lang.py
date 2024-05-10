import streamlit as st

class Translations(dict):
    def __init__(self, d, s="en"):
        super().__init__(d)
        self.__dict__ = {k.lower(): v for k, v in d.items()}
        self.s = s
    def __getitem__(self, key):
        key = key.lower()
        word_trad = self.__dict__.get(key, key)
        if isinstance(word_trad, dict):
            return word_trad.get(self.s, key)
        return word_trad

t = {
    "home": {
        "en": "Home",
        "es": "Inicio",
        "fr": "Accueil",
        "de": "Zuhause",
        "it": "Casa",
        "pt": "Casa",
        "ja": "ホーム",
        "ko": "집",
        "zh": "家",
    },
    "database Management": {
        "en": "Database Management",
        "es": "Gestión de la base de datos",
        "fr": "Gestion de base de données",
        "de": "Datenbankverwaltung",
        "it": "Gestione del database",
        "pt": "Gerenciamento de banco de dados",
        "ja": "データベース管理",
        "ko": "데이터베이스 관리",
        "zh": "数据库管理",
    },
    "title": {
        "en": "Food Traceability Database Management",
        "es": "Gestión de la base de datos de trazabilidad de alimentos",
        "fr": "Gestion de base de données de traçabilité alimentaire",
        "de": "Lebensmittel-Rückverfolgungsdatenbankverwaltung",
        "it": "Gestione del database di tracciabilità alimentare",
        "pt": "Gerenciamento de banco de dados de rastreabilidade de alimentos",
        "ja": "食品トレーサビリティデータベース管理",
        "ko": "식품 추적 데이터베이스 관리",
        "zh": "食品追溯数据库管理",
    },
    "software name": {
        "en": "Big Food",
        "es": "Gran comida",
        "fr": "Grande nourriture",
        "de": "Große Lebensmittel",
        "it": "Big Food",
        "pt": "Grande comida",
        "ja": "ビッグフード",
        "ko": "빅 푸드",
        "zh": "大食品",
    },
    "add filter": {
        "en": "Add filter",
        "es": "Agregar filtro",
        "fr": "Ajouter un filtre",
        "de": "Filter hinzufügen",
        "it": "Aggiungi filtro",
        "pt": "Adicionar filtro",
        "ja": "フィルターを追加",
        "ko": "필터 추가",
        "zh": "添加过滤器",
    },
    "filter dataframe on": {
        "en": "Filter dataframe on",
        "es": "Filtrar dataframe en",
        "fr": "Filtrer le dataframe sur",
        "de": "Filter-Datenrahmen auf",
        "it": "Filtra il dataframe su",
        "pt": "Filtrar dataframe em",
        "ja": "データフレームをフィルタリングする",
        "ko": "데이터 프레임 필터링",
        "zh": "过滤数据框",
    },
    "semi-finished products": {
        "en": "Semi-Finished Products",
        "es": "Productos Semielaborados",
        "fr": "Produits Semi-finis",
        "de": "Halbfertige Produkte",
        "it": "Prodotti Semilavorati",
        "pt": "Produtos Semiacabados",
        "ja": "半製品",
        "ko": "준설제",
        "zh": "半成品",
    },
    "add semi-finished Product": {
        "en": "Add Semi-Finished Product",
        "es": "Agregar Producto Semielaborado",
        "fr": "Ajouter un Produit Semi-fini",
        "de": "Halbfertiges Produkt hinzufügen",
        "it": "Aggiungi Prodotto Semilavorato",
        "pt": "Adicionar Produto Semiacabado",
        "ja": "半製品を追加",
        "ko": "준설제 추가",
        "zh": "添加半成品",
    },
    "raw materials": {
        "en": "Raw Materials",
        "es": "Materias Primas",
        "fr": "Matières Premières",
        "de": "Rohstoffe",
        "it": "Materie Prime",
        "pt": "Matérias-Primas",
        "ja": "原材料",
        "ko": "원자재",
        "zh": "原材料",
    },
    "suppliers": {
        "en": "Suppliers",
        "es": "Proveedores",
        "fr": "Fournisseurs",
        "de": "Lieferanten",
        "it": "Fornitori",
        "pt": "Fornecedores",
        "ja": "サプライヤー",
        "ko": "공급 업체",
        "zh": "供应商",
    },
    "add row material": {
        "en": "Add Row Material",
        "es": "Agregar Materia Prima",
        "fr": "Ajouter une Matière Première",
        "de": "Rohstoff hinzufügen",
        "it": "Aggiungi Materia Prima",
        "pt": "Adicionar Matéria Prima",
        "ja": "原材料を追加",
        "ko": "원자재 추가",
        "zh": "添加原材料",
    },
    "name": {
        "en": "Name",
        "es": "Nombre",
        "fr": "Nom",
        "de": "Name",
        "it": "Nome",
        "pt": "Nome",
        "ja": "名前",
        "ko": "이름",
        "zh": "名称",
    },
    "supplier name": {
        "en": "Supplier name",
        "es": "Nombre del proveedor",
        "fr": "Nom du fournisseur",
        "de": "Lieferantenname",
        "it": "Nome del fornitore",
        "pt": "Nome do fornecedor",
        "ja": "サプライヤー名",
        "ko": "공급 업체 이름",
        "zh": "供应商名称",
    },
    "supplier address": {
        "en": "Supplier address",
        "es": "Dirección del proveedor",
        "fr": "Adresse du fournisseur",
        "de": "Lieferantenadresse",
        "it": "Indirizzo del fornitore",
        "pt": "Endereço do fornecedor",
        "ja": "サプライヤーの住所",
        "ko": "공급 업체 주소",
        "zh": "供应商地址",
    },
    "production date": {
        "en": "production date",
        "es": "fecha de producción",
        "fr": "date de production",
        "de": "Produktionsdatum",
        "it": "data di produzione",
        "pt": "data de produção",
        "ja": "製造日",
        "ko": "생산 일",
        "zh": "生产日期",
    },
    "acquiring date": {
        "en": "acquiring date",
        "es": "fecha de adquisición",
        "fr": "date d'acquisition",
        "de": "Erwerbsdatum",
        "it": "data di acquisizione",
        "pt": "data de aquisição",
        "ja": "取得日",
        "ko": "획득 날짜",
        "zh": "获取日期",
    },
    "expiration date": {
        "en": "expiration date",
        "es": "fecha de caducidad",
        "fr": "date d'expiration",
        "de": "Verfallsdatum",
        "it": "data di scadenza",
        "pt": "data de validade",
        "ja": "有効期限",
        "ko": "유통 기한",
        "zh": "有效期",
    },
    "batch number": {
        "en": "Batch number",
        "es": "Número de lote",
        "fr": "Numéro de lot",
        "de": "Chargennummer",
        "it": "Numero di lotto",
        "pt": "Número do lote",
        "ja": "バッチ番号",
        "ko": "배치 번호",
        "zh": "批号",
    },
    "supplier batch number": {
        "en": "Supplier batch number",
        "es": "Número de lote del proveedor",
        "fr": "Numéro de lot du fournisseur",
        "de": "Lieferantenchargennummer",
        "it": "Numero di lotto del fornitore",
        "pt": "Número do lote do fornecedor",
        "ja": "サプライヤーバッチ番号",
        "ko": "공급 업체 일괄 번호",
        "zh": "供应商批号",
    },
    "document number": {
        "en": "Document number",
        "es": "Número de documento",
        "fr": "Numéro de document",
        "de": "Dokumentnummer",
        "it": "Numero di documento",
        "pt": "Número do documento",
        "ja": "文書番号",
        "ko": "문서 번호",
        "zh": "文件编号",
    },
    "quantity": {
        "en": "Quantity",
        "es": "Cantidad",
        "fr": "Quantité",
        "de": "Menge",
        "it": "Quantità",
        "pt": "Quantidade",
        "ja": "量",
        "ko": "수량",
        "zh": "数量",
    },
    "unit": {
        "en": "Unit",
        "es": "Unidad",
        "fr": "Unité",
        "de": "Einheit",
        "it": "Unità",
        "pt": "Unidade",
        "ja": "単位",
        "ko": "단위",
        "zh": "单位",
    },
    "raw material added successfully": {
        "en": "Raw material added successfully",
        "es": "Materia prima agregada con éxito",
        "fr": "Matière première ajoutée avec succès",
        "de": "Rohstoff erfolgreich hinzugefügt",
        "it": "Materia prima aggiunta con successo",
        "pt": "Matéria-prima adicionada com sucesso",
        "ja": "原材料が正常に追加されました",
        "ko": "원자재가 성공적으로 추가되었습니다",
        "zh": "原材料成功添加",
    },
    "modify data": {
        "en": "Modify Data",
        "es": "Modificar Datos",
        "fr": "Modifier les données",
        "de": "Daten ändern",
        "it": "Modifica dati",
        "pt": "Modificar dados",
        "ja": "データを変更",
        "ko": "데이터 수정",
        "zh": "修改数据",
    },
    "data modified successfully": {
        "en": "Data modified successfully",
        "es": "Datos modificados con éxito",
        "fr": "Données modifiées avec succès",
        "de": "Daten erfolgreich geändert",
        "it": "Dati modificati con successo",
        "pt": "Dados modificados com sucesso",
        "ja": "データが正常に変更されました",
        "ko": "데이터가 성공적으로 수정되었습니다",
        "zh": "数据成功修改",
    },
    "address": {
        "en": "Address",
        "es": "Dirección",
        "fr": "Adresse",
        "de": "Adresse",
        "it": "Indirizzo",
        "pt": "Endereço",
        "ja": "住所",
        "ko": "주소",
        "zh": "地址",
    },
    "phone number": {
        "en": "Phone number",
        "es": "Número de teléfono",
        "fr": "Numéro de téléphone",
        "de": "Telefonnummer",
        "it": "Numero di telefono",
        "pt": "Número de telefone",
        "ja": "電話番号",
        "ko": "전화 번호",
        "zh": "电话号码",
    },
    "email": {
        "en": "Email",
        "es": "Correo electrónico",
        "fr": "Email",
        "de": "Email",
        "it": "E-mail",
        "pt": "E-mail",
        "ja": "Eメール",
        "ko": "이메일",
        "zh": "电子邮件",
    },
    "supplier already exists": {
        "en": "Supplier already exists",
        "es": "Proveedor ya existe",
        "fr": "Le fournisseur existe déjà",
        "de": "Lieferant existiert bereits",
        "it": "Il fornitore esiste già",
        "pt": "Fornecedor já existe",
        "ja": "サプライヤーはすでに存在します",
        "ko": "공급 업체가 이미 존재합니다",
        "zh": "供应商已经存在",
    },
    "supplier added successfully": {
        "en": "Supplier added successfully",
        "es": "Proveedor agregado con éxito",
        "fr": "Fournisseur ajouté avec succès",
        "de": "Lieferant erfolgreich hinzugefügt",
        "it": "Fornitore aggiunto con successo",
        "pt": "Fornecedor adicionado com sucesso",
        "ja": "サプライヤーが正常に追加されました",
        "ko": "공급 업체가 성공적으로 추가되었습니다",
        "zh": "供应商成功添加",
    },
    "How many Raw Material?": {
        "en": "How many Raw Material?",
        "es": "¿Cuánta materia prima?",
        "fr": "Combien de matières premières?",
        "de": "Wie viele Rohstoffe?",
        "it": "Quante materie prime?",
        "pt": "Quantos materiais brutos?",
        "ja": "原材料はいくつですか？",
        "ko": "원자재는 몇 개입니까?",
        "zh": "原材料有多少？",
    },
    "How many Semi-Finished Products?": {
        "en": "How many Semi-Finished Products?",
        "es": "¿Cuántos productos semielaborados?",
        "fr": "Combien de produits semi-finis?",
        "de": "Wie viele Halbfertigprodukte?",
        "it": "Quanti prodotti semilavorati?",
        "pt": "Quantos produtos semi-acabados?",
        "ja": "半製品はいくつですか？",
        "ko": "준설제는 몇 개입니까?",
        "zh": "半成品有多少？",
    },
    "Ingredients": {
        "en": "Ingredients",
        "es": "Ingredientes",
        "fr": "Ingrédients",
        "de": "Zutaten",
        "it": "Ingredienti",
        "pt": "Ingredientes",
        "ja": "材料",
        "ko": "성분",
        "zh": "成分",
    },
    "Ingredient": {
        "en": "Ingredient",
        "es": "Ingrediente",
        "fr": "Ingrédient",
        "de": "Zutat",
        "it": "Ingrediente",
        "pt": "Ingrediente",
        "ja": "材料",
        "ko": "성분",
        "zh": "成分",
    },
    "Done": {
        "en": "Done",
        "es": "Hecho",
        "fr": "Terminé",
        "de": "Erledigt",
        "it": "Fatto",
        "pt": "Feito",
        "ja": "完了",
        "ko": "완료",
        "zh": "完成",
    },
    "Search": {
        "en": "Search",
        "es": "Buscar",
        "fr": "Chercher",
        "de": "Suche",
        "it": "Ricerca",
        "pt": "Procurar",
        "ja": "検索",
        "ko": "검색",
        "zh": "搜索",
    },
    "Load Selected": {
        "en": "Load Selected",
        "es": "Cargar Seleccionado",
        "fr": "Charger Sélectionné",
        "de": "Ausgewähltes Laden",
        "it": "Carica Selezionato",
        "pt": "Carregar Selecionado",
        "ja": "選択したものを読み込む",
        "ko": "선택된 항목로드",
        "zh": "加载所选",
    },
    "Delete Selected": {
        "en": "Delete Selected",
        "es": "Eliminar Seleccionado",
        "fr": "Supprimer Sélectionné",
        "de": "Ausgewähltes Löschen",
        "it": "Elimina Selezionato",
        "pt": "Excluir Selecionado",
        "ja": "選択したものを削除",
        "ko": "선택된 항목 삭제",
        "zh": "删除所选",
    },
    "Delete this product": {
        "en": "Delete this product",
        "es": "Eliminar este producto",
        "fr": "Supprimer ce produit",
        "de": "Dieses Produkt löschen",
        "it": "Elimina questo prodotto",
        "pt": "Excluir este produto",
        "ja": "この製品を削除",
        "ko": "이 제품 삭제",
        "zh": "删除此产品",
    },
    "Add Raw Material": {
        "en": "Add Raw Material",
        "es": "Agregar Materia Prima",
        "fr": "Ajouter une matière première",
        "de": "Rohstoff hinzufügen",
        "it": "Aggiungi materia prima",
        "pt": "Adicionar matéria-prima",
        "ja": "原材料を追加",
        "ko": "원자재 추가",
        "zh": "添加原材料",
    },
    "Add Supplier": {
        "en": "Add Supplier",
        "es": "Agregar Proveedor",
        "fr": "Ajouter un fournisseur",
        "de": "Lieferant hinzufügen",
        "it": "Aggiungi fornitore",
        "pt": "Adicionar fornecedor",
        "ja": "サプライヤーを追加",
        "ko": "공급 업체 추가",
        "zh": "添加供应商",
    },
    "Products and Semi-finished Products": {
        "en": "Products and Semi-finished Products",
        "es": "Productos y productos semielaborados",
        "fr": "Produits et produits semi-finis",
        "de": "Produkte und Halbfertigprodukte",
        "it": "Prodotti e semilavorati",
        "pt": "Produtos e produtos semi-acabados",
        "ja": "製品と半製品",
        "ko": "제품 및 준설제",
        "zh": "产品和半成品",
    },
    "Data Entry": {
        "en": "Data Entry",
        "es": "Entrada de datos",
        "fr": "Saisie de données",
        "de": "Dateneingabe",
        "it": "Inserimento dati",
        "pt": "Entrada de dados",
        "ja": "データ入力",
        "ko": "데이터 입력",
        "zh": "数据输入",
    },
    "Modify Data": {
        "en": "Modify Data",
        "es": "Modificar Datos",
        "fr": "Modifier les données",
        "de": "Daten ändern",
        "it": "Modifica dati",
        "pt": "Modificar dados",
        "ja": "データを変更",
        "ko": "데이터 수정",
        "zh": "修改数据",
    },
    "Data Visualization": {
        "en": "Data Visualization",
        "es": "Visualización de datos",
        "fr": "Visualisation des données",
        "de": "Datenvisualisierung",
        "it": "Visualizzazione dei dati",
        "pt": "Visualização de dados",
        "ja": "データ可視化",
        "ko": "데이터 시각화",
        "zh": "数据可视化",
    },
    "Field": {
        "en": "Field",
        "es": "Campo",
        "fr": "Champ",
        "de": "Feld",
        "it": "Campo",
        "pt": "Campo",
        "ja": "フィールド",
        "ko": "분야",
        "zh": "领域",
    },
    "Value": {
        "en": "Value",
        "es": "Valor",
        "fr": "Valeur",
        "de": "Wert",
        "it": "Valore",
        "pt": "Valor",
        "ja": "値",
        "ko": "값",
        "zh": "值",
    },
    "Select Semi-Finished Product": {
        "en": "Select Semi-Finished Product",
        "es": "Seleccionar producto semielaborado",
        "fr": "Sélectionner un produit semi-fini",
        "de": "Halbfertiges Produkt auswählen",
        "it": "Seleziona prodotto semilavorato",
        "pt": "Selecionar produto semi-acabado",
        "ja": "半製品を選択",
        "ko": "준설제 선택",
        "zh": "选择半成品",
    },
    "Select Raw Material": {
        "en": "Select Raw Material",
        "es": "Seleccionar materia prima",
        "fr": "Sélectionner une matière première",
        "de": "Rohstoff auswählen",
        "it": "Seleziona materia prima",
        "pt": "Selecionar matéria-prima",
        "ja": "原材料を選択",
        "ko": "원자재 선택",
        "zh": "选择原材料",
    },
    "manual input": {
        "en": "Manual Input",
        "es": "Entrada manual",
        "fr": "Entrée manuelle",
        "de": "Manuelle Eingabe",
        "it": "Inserimento manuale",
        "pt": "Entrada manual",
        "ja": "手動入力",
        "ko": "수동 입력",
        "zh": "手动输入",
    },
}
def get_translations(lang_choice="en"):
    trad = Translations(t, lang_choice)
    if 'trad' not in st.session_state:
        st.session_state['trad'] = trad
    trad = st.session_state['trad']
    return trad
lang_choice = 'it'
# italian date time format
datetime_format = "DD/MM/YYYY"
