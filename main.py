# main.py

import logging
import os
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from dotenv import load_dotenv

# It's a good practice to load sensitive data from a .env file
load_dotenv()

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Make sure your NOWPayments API key is in your .env file
CRYPTO_PAYMENT_API_KEY = os.getenv("CRYPTO_PAYMENT_API_KEY") 
# Using the correct 'invoice' endpoint to get a payment URL
CRYPTO_PAYMENT_API_URL = "https://api.nowpayments.io/v1/invoice"

# --- Logging Setup ---
# Enable logging to see errors and debug information
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Translation Data ---
TRANSLATIONS = {
    'en': {
        'welcome': "hi to cards.cc\nPlease choose the country of the card you want:",
        'choose_card_type': "Please choose a card type for {country_name}:",
        'back_to_countries': "« Back to Countries",
        'available_cards': "Here is available cards:",
        'number': "Number:", 'expiry': "Expiry:", 'cvc': "CVC:", 'full_name': "Full Name:",
        'dob': "Date of birth:", 'address': "Address:", 'state': "State:", 'city': "City:",
        'zip_code': "Zip Code:", 'country': "Country:", 'phone': "Phone number:",
        'bank_name': "Bank Name:", 'price': "Price:",
        'buy_for': "Buy for ${price}", 'change_card': "♻️ Change the card",
        'back_to_card_types': "« Back to Card Types",
        'purchase_prompt': "To purchase your {product_name}, please complete the payment using the link below:",
        'payment_success_remark': "(After you successfully make the payment, you will receive the card details here in the chat)",
        'country_names': {"us": "USA 🇺🇸", "gb": "UK 🇬🇧", "fr": "France 🇫🇷", "ca": "Canada 🇨🇦", "de": "Germany 🇩🇪", "au": "Australia 🇦🇺", "jp": "Japan 🇯🇵"},
        'banks': {"us": ["Chase Bank", "Bank of America"], "gb": ["HSBC", "Barclays"], "fr": ["BNP Paribas", "Société Générale"], "ca": ["RBC", "TD Bank"], "de": ["Deutsche Bank", "Commerzbank"], "au": ["Commonwealth Bank", "Westpac"], "jp": ["MUFG Bank", "SMBC"]}
    },
    'fr': {
        'welcome': "Salut sur cards.cc\nVeuillez choisir le pays de la carte que vous souhaitez :",
        'choose_card_type': "Veuillez choisir un type de carte pour {country_name}:",
        'back_to_countries': "« Retour aux pays",
        'available_cards': "Voici les cartes disponibles :",
        'number': "Numéro:", 'expiry': "Expiration:", 'cvc': "CVC:", 'full_name': "Nom complet:",
        'dob': "Date de naissance:", 'address': "Adresse:", 'state': "État/Région:", 'city': "Ville:",
        'zip_code': "Code postal:", 'country': "Pays:", 'phone': "Téléphone:",
        'bank_name': "Banque:", 'price': "Prix:",
        'buy_for': "Acheter pour ${price}", 'change_card': "♻️ Changer la carte",
        'back_to_card_types': "« Retour aux types de cartes",
        'purchase_prompt': "Pour acheter votre {product_name}, veuillez effectuer le paiement via le lien ci-dessous :",
        'payment_success_remark': "(Une fois le paiement effectué avec succès, vous recevrez les détails de la carte ici dans le chat)",
        'country_names': {"us": "États-Unis 🇺🇸", "gb": "Royaume-Uni 🇬🇧", "fr": "France 🇫🇷", "ca": "Canada 🇨🇦", "de": "Allemagne �🇪", "au": "Australie 🇦🇺", "jp": "Japon 🇯🇵"},
        'banks': {"us": ["Chase Bank", "Bank of America"], "gb": ["HSBC", "Barclays"], "fr": ["BNP Paribas", "Société Générale"], "ca": ["RBC", "TD Bank"], "de": ["Deutsche Bank", "Commerzbank"], "au": ["Commonwealth Bank", "Westpac"], "jp": ["MUFG Bank", "SMBC"]}
    },
    'es': {
        'welcome': "Hola en cards.cc\nPor favor, elige el país de la tarjeta que deseas:",
        'choose_card_type': "Por favor, elige un tipo de tarjeta para {country_name}:",
        'back_to_countries': "« Volver a países",
        'available_cards': "Aquí están las tarjetas disponibles:",
        'number': "Número:", 'expiry': "Vencimiento:", 'cvc': "CVC:", 'full_name': "Nombre completo:",
        'dob': "Fecha de nacimiento:", 'address': "Dirección:", 'state': "Estado/Provincia:", 'city': "Ciudad:",
        'zip_code': "Código postal:", 'country': "País:", 'phone': "Teléfono:",
        'bank_name': "Banco:", 'price': "Precio:",
        'buy_for': "Comprar por ${price}", 'change_card': "♻️ Cambiar la tarjeta",
        'back_to_card_types': "« Volver a tipos de tarjeta",
        'purchase_prompt': "Para comprar tu {product_name}, completa el pago usando el siguiente enlace:",
        'payment_success_remark': "(Después de realizar el pago con éxito, recibirás los detalles de la tarjeta aquí en el chat)",
        'country_names': {"us": "EE.UU. 🇺🇸", "gb": "Reino Unido 🇬🇧", "fr": "Francia 🇫🇷", "ca": "Canadá 🇨🇦", "de": "Alemania 🇩🇪", "au": "Australia 🇦🇺", "jp": "Japón 🇯🇵"},
        'banks': {"us": ["Chase Bank", "Bank of America"], "gb": ["HSBC", "Barclays"], "fr": ["BNP Paribas", "Société Générale"], "ca": ["RBC", "TD Bank"], "de": ["Deutsche Bank", "Commerzbank"], "au": ["Commonwealth Bank", "Westpac"], "jp": ["MUFG Bank", "SMBC"]}
    },
    'ru': {
        'welcome': "Привет в cards.cc\nПожалуйста, выберите страну карты, которую вы хотите:",
        'choose_card_type': "Пожалуйста, выберите тип карты для {country_name}:",
        'back_to_countries': "« Назад к странам",
        'available_cards': "Вот доступные карты:",
        'number': "Номер:", 'expiry': "Срок действия:", 'cvc': "CVC:", 'full_name': "Полное имя:",
        'dob': "Дата рождения:", 'address': "Адрес:", 'state': "Штат/Регион:", 'city': "Город:",
        'zip_code': "Почтовый индекс:", 'country': "Страна:", 'phone': "Телефон:",
        'bank_name': "Банк:", 'price': "Цена:",
        'buy_for': "Купить за ${price}", 'change_card': "♻️ Сменить карту",
        'back_to_card_types': "« Назад к типам карт",
        'purchase_prompt': "Чтобы приобрести {product_name}, пожалуйста, совершите платеж по ссылке ниже:",
        'payment_success_remark': "(После успешной оплаты вы получите данные карты здесь, в чате)",
        'country_names': {"us": "США 🇺🇸", "gb": "Великобритания 🇬🇧", "fr": "Франция 🇫🇷", "ca": "Канада 🇨🇦", "de": "Германия 🇩🇪", "au": "Австралия 🇦🇺", "jp": "Япония 🇯🇵"},
        'banks': {"us": ["Chase Bank", "Bank of America"], "gb": ["HSBC", "Barclays"], "fr": ["BNP Paribas", "Société Générale"], "ca": ["RBC", "TD Bank"], "de": ["Deutsche Bank", "Commerzbank"], "au": ["Commonwealth Bank", "Westpac"], "jp": ["MUFG Bank", "SMBC"]}
    },
    'zh': {
        'welcome': "欢迎来到 cards.cc\n请选择您想要的卡的国家:",
        'choose_card_type': "请为 {country_name} 选择卡类型:",
        'back_to_countries': "« 返回国家列表",
        'available_cards': "可用卡片如下:",
        'number': "卡号:", 'expiry': "有效期:", 'cvc': "CVC:", 'full_name': "全名:",
        'dob': "出生日期:", 'address': "地址:", 'state': "州/省:", 'city': "城市:",
        'zip_code': "邮政编码:", 'country': "国家:", 'phone': "电话号码:",
        'bank_name': "银行名称:", 'price': "价格:",
        'buy_for': "购买价格 ${price}", 'change_card': "♻️ 更换卡片",
        'back_to_card_types': "« 返回卡类型",
        'purchase_prompt': "要购买您的 {product_name}，请使用以下链接完成付款：",
        'payment_success_remark': "(成功付款后，您将在此聊天中收到卡片详细信息)",
        'country_names': {"us": "美国 🇺🇸", "gb": "英国 🇬🇧", "fr": "法国 🇫🇷", "ca": "加拿大 🇨🇦", "de": "德国 🇩🇪", "au": "澳大利亚 🇦🇺", "jp": "日本 🇯🇵"},
        'banks': {"us": ["Chase Bank", "Bank of America"], "gb": ["HSBC", "Barclays"], "fr": ["BNP Paribas", "Société Générale"], "ca": ["RBC", "TD Bank"], "de": ["Deutsche Bank", "Commerzbank"], "au": ["Commonwealth Bank", "Westpac"], "jp": ["MUFG Bank", "SMBC"]}
    },
    'ar': {
        'welcome': "أهلاً بك في cards.cc\nالرجاء اختيار بلد البطاقة التي تريدها:",
        'choose_card_type': "الرجاء اختيار نوع البطاقة لـ {country_name}:",
        'back_to_countries': "« العودة إلى البلدان",
        'available_cards': "البطاقات المتاحة:",
        'number': "الرقم:", 'expiry': "انتهاء الصلاحية:", 'cvc': "CVC:", 'full_name': "الاسم الكامل:",
        'dob': "تاريخ الميلاد:", 'address': "العنوان:", 'state': "الولاية/المقاطعة:", 'city': "المدينة:",
        'zip_code': "الرمز البريدي:", 'country': "البلد:", 'phone': "رقم الهاتف:",
        'bank_name': "اسم البنك:", 'price': "السعر:",
        'buy_for': "شراء مقابل ${price}", 'change_card': "♻️ تغيير البطاقة",
        'back_to_card_types': "« العودة إلى أنواع البطاقات",
        'purchase_prompt': "لشراء {product_name}، يرجى إكمال الدفع باستخدام الرابط أدناه:",
        'payment_success_remark': "(بعد إتمام الدفع بنجاح، ستتلقى تفاصيل البطاقة هنا في الدردشة)",
        'country_names': {"us": "الولايات المتحدة 🇺🇸", "gb": "المملكة المتحدة 🇬🇧", "fr": "فرنسا 🇫🇷", "ca": "كندا 🇨🇦", "de": "ألمانيا 🇩🇪", "au": "أستراليا 🇦🇺", "jp": "اليابان 🇯🇵"},
        'banks': {"us": ["Chase Bank", "Bank of America"], "gb": ["HSBC", "Barclays"], "fr": ["BNP Paribas", "Société Générale"], "ca": ["RBC", "TD Bank"], "de": ["Deutsche Bank", "Commerzbank"], "au": ["Commonwealth Bank", "Westpac"], "jp": ["MUFG Bank", "SMBC"]}
    }
}

# --- Product Data ---
CARD_TYPES = {"us": ["visa", "mastercard", "discover", "amex"], "gb": ["visa", "mastercard"], "fr": ["visa", "mastercard"], "ca": ["visa", "mastercard"], "de": ["visa", "mastercard"], "au": ["visa", "mastercard"], "jp": ["visa", "mastercard"]}

# --- Helper Functions ---
def escape_markdown_v2(text: str) -> str:
    """Escapes characters for Telegram's MarkdownV2 parser."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def t(key: str, context: ContextTypes.DEFAULT_TYPE, **kwargs) -> str:
    """Translates a given key based on the user's language."""
    lang = context.user_data.get('lang', 'en')
    template = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, f"_{key}_")
    return template.format(**kwargs)

def generate_card_details(country_code, card_type, context):
    """Generates random card details including address from an API."""
    full_name, dob, phone, city, state, zip_code = "(HIDDEN)", "(N/A)", "(HIDDEN)", "(N/A)", "(N/A)", "(N/A)"
    try:
        response = requests.get(f"https://randomuser.me/api/?nat={country_code}")
        response.raise_for_status()
        data = response.json()["results"][0]
        location = data["location"]
        city, state, zip_code = location["city"], location["state"], location["postcode"]
        dob_iso = data["dob"]["date"]
        dob_obj = datetime.fromisoformat(dob_iso.replace('Z', '+00:00'))
        dob = dob_obj.strftime("%d/%m/%Y")
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not fetch random address: {e}")

    card_number = f"**** ****** {random.randint(10000, 99999)}" if card_type == "amex" else f"**** **** **** {random.randint(1000, 9999)}"
    exp_date = f"{random.randint(1, 12):02d}/{str(random.randint(datetime.now().year + 1, datetime.now().year + 5))[-2:]}"
    price = random.randint(20, 50)
    lang = context.user_data.get('lang', 'en')
    country_banks = TRANSLATIONS.get(lang, TRANSLATIONS['en'])['banks'].get(country_code, ["Global Union Bank"])
    bank_name = random.choice(country_banks)

    return card_number, exp_date, "***", price, city, state, zip_code, bank_name, full_name, dob, phone

# --- Bot UI Functions ---
async def show_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the country selection menu."""
    lang = context.user_data.get('lang', 'en')
    country_names = TRANSLATIONS.get(lang, TRANSLATIONS['en'])['country_names']
    keyboard = [
        [InlineKeyboardButton(country_names["us"], callback_data="country_us"), InlineKeyboardButton(country_names["gb"], callback_data="country_gb"), InlineKeyboardButton(country_names["fr"], callback_data="country_fr")],
        [InlineKeyboardButton(country_names["ca"], callback_data="country_ca"), InlineKeyboardButton(country_names["de"], callback_data="country_de"), InlineKeyboardButton(country_names["au"], callback_data="country_au")],
        [InlineKeyboardButton(country_names["jp"], callback_data="country_jp")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text=t('welcome', context), reply_markup=reply_markup)

# --- Bot Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message with language selection buttons."""
    welcome_message = "Please select your language / الرجاء اختيار لغتك"
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"), InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")],
        [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"), InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh"), InlineKeyboardButton("🇦🇪 العربية", callback_data="lang_ar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup)

# --- Callback Query Handler ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses all CallbackQueries for the multi-step menu."""
    query = update.callback_query
    await query.answer()
    query_data = query.data
    
    parts = query_data.split("_")
    action = parts[0]

    if action == "lang":
        context.user_data['lang'] = parts[1]
        await show_countries(update, context)

    elif action == "country":
        country_code = parts[1]
        lang = context.user_data.get('lang', 'en')
        country_name = TRANSLATIONS[lang]['country_names'].get(country_code, "")
        keyboard = [[InlineKeyboardButton(card_type.upper(), callback_data=f"cardtype_{country_code}_{card_type}")] for card_type in CARD_TYPES.get(country_code, [])]
        keyboard.append([InlineKeyboardButton(t('back_to_countries', context), callback_data="back_start")])
        await query.edit_message_text(text=t('choose_card_type', context, country_name=country_name), reply_markup=InlineKeyboardMarkup(keyboard))

    elif action == "cardtype":
        country_code, card_type = parts[1], parts[2]
        lang = context.user_data.get('lang', 'en')
        country_name = TRANSLATIONS[lang]['country_names'].get(country_code, "")
        card_number, exp_date, cvc, price, city, state, zip_code, bank_name, full_name, dob, phone = generate_card_details(country_code, card_type, context)
        
        # Escape all dynamic values before inserting them into the message
        card_details_text = (
            f"*{escape_markdown_v2(t('available_cards', context))}*\n\n"
            f"*{escape_markdown_v2(t('number', context))}* `{escape_markdown_v2(card_number)}`\n"
            f"*{escape_markdown_v2(t('expiry', context))}* `{escape_markdown_v2(exp_date)}`\n"
            f"*{escape_markdown_v2(t('cvc', context))}* `{escape_markdown_v2(cvc)}`\n"
            f"*{escape_markdown_v2(t('full_name', context))}* `{escape_markdown_v2(full_name)}`\n"
            f"*{escape_markdown_v2(t('dob', context))}* `{escape_markdown_v2(dob)}`\n"
            f"*{escape_markdown_v2(t('address', context))}* `\\(HIDDEN\\)`\n"
            f"*{escape_markdown_v2(t('state', context))}* `{escape_markdown_v2(state)}`\n"
            f"*{escape_markdown_v2(t('city', context))}* `{escape_markdown_v2(city)}`\n"
            f"*{escape_markdown_v2(t('zip_code', context))}* `{escape_markdown_v2(str(zip_code))}`\n"
            f"*{escape_markdown_v2(t('country', context))}* `{escape_markdown_v2(country_name)}`\n"
            f"*{escape_markdown_v2(t('phone', context))}* `\\(HIDDEN\\)`\n\n"
            f"*{escape_markdown_v2(t('bank_name', context))}* `{escape_markdown_v2(bank_name)}`\n\n"
            f"*{escape_markdown_v2(t('price', context))}* *${price}*"
        )
        keyboard = [
            [InlineKeyboardButton(t('buy_for', context, price=price), callback_data=f"buy_{country_code}_{card_type}_{price}")],
            [InlineKeyboardButton(t('change_card', context), callback_data=f"cardtype_{country_code}_{card_type}")],
            [InlineKeyboardButton(t('back_to_card_types', context), callback_data=f"country_{country_code}")]
        ]
        await query.edit_message_text(text=card_details_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='MarkdownV2')

    elif action == "back":
        await start(update, context)

    elif action == "buy":
        country_code, card_type, price = parts[1], parts[2], int(parts[3])
        lang = context.user_data.get('lang', 'en')
        product_name = f"{TRANSLATIONS[lang]['country_names'].get(country_code).split(' ')[0]} {card_type.capitalize()} Card"
        try:
            headers = {"x-api-key": CRYPTO_PAYMENT_API_KEY, "Content-Type": "application/json"}
            payload = {"price_amount": price, "price_currency": "usd", "order_id": f"product_{country_code}_{card_type}_{update.effective_user.id}", "order_description": product_name}
            response = requests.post(CRYPTO_PAYMENT_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            payment_data = response.json()
            if payment_url := payment_data.get("invoice_url"):
                # Escape the URL and other text for MarkdownV2
                escaped_url = escape_markdown_v2(payment_url)
                escaped_prompt = escape_markdown_v2(t('purchase_prompt', context, product_name=product_name))
                escaped_remark = escape_markdown_v2(t('payment_success_remark', context))
                
                purchase_message = (
                    f"{escaped_prompt}\n\n"
                    f"{escaped_url}\n\n"
                    f"_{escaped_remark}_"
                )
                await query.edit_message_text(text=purchase_message, parse_mode='MarkdownV2')
            else:
                logger.error(f"Unexpected response from NOWPayments: {payment_data}")
                await query.edit_message_text(text=f"Unexpected response: `{str(payment_data)}`")
        except requests.exceptions.HTTPError as e:
            error_message = e.response.json().get("message", "HTTP error")
            logger.error(f"HTTP Error: {e.response.status_code} - {error_message}")
            await query.edit_message_text(text=f"Error: {error_message}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            await query.edit_message_text(text=f"An unexpected error occurred. Details: {e}")

# --- Main Bot Logic ---
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    elif not CRYPTO_PAYMENT_API_KEY:
        logger.error("CRYPTO_PAYMENT_API_KEY environment variable not set. Cannot process payments.")
    else:
        main()
