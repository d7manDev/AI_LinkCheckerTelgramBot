import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackContext, CallbackQueryHandler
import datetime
import validators

# تعيين مفتاح API لـ OpenAI
openai.api_key = "Your_Openai_Api"  # استبدل بمفتاح API الخاص بك

# تعيين توكن بوت تليجرام
TELEGRAM_BOT_TOKEN = "Your_Bot_Token"  # استبدل بتوكن البوت الخاص بك
# متغير لتخزين معلومات المستخدمين والروابط
user_data = []
# المستخدم الذي يعتبر مدير البوت (يجب تعديله وفقاً للمعرف الفعلي للمدير)
ADMIN_USER_ID = Your_Telgram_User_ID
# تكوين المستخدم (اختياري)
# USER_ID = 123456789  # استبدل بمعرف المستخدم الخاص بك
control_panel_displayed = False

# دالة بداية الدردشة
def start(update: Update, context: CallbackContext) -> None:
    # تحقق مما إذا كان المتغير معرفًا مسبقًا، وإلا قم بتعريفه
    if 'connected_users' not in context.bot_data:
        context.bot_data['connected_users'] = 0

    # زيادة عدد المستخدمين المتصلين بواحد
    context.bot_data['connected_users'] += 1

    
    user_info = {
        'user_id': update.message.from_user.id,
        'username': update.message.from_user.username,
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'links': []
    }
    user_data.append(user_info)
    # قائمة الأوامر للقائمة الجانبية
    commands = [
        ['/stats', '/help'],  # يمكنك إضافة المزيد إذا كنت بحاجة
    ]

    # إعداد زرارات القائمة الجانبية
    reply_markup = ReplyKeyboardMarkup(commands, one_time_keyboard=True)

    # إذا كان المستخدم هو المدير
    if update.message.from_user.id == ADMIN_USER_ID:
        # رسالة ترحيبية خاصة للمدير
        welcome_message = f'أهلاً بك، ({update.message.from_user.username})! كمدير للبوت، يمكنك استخدام الأوامر الخاصة بك.'
        update.message.reply_text(welcome_message)
    else:
        # رسالة ترحيب عادية للمستخدم العادي
        welcome_message = f'أهلاً بك، ({update.message.from_user.username})! قم بإرسال الرابط الذي تريد فحصه.'
        update.message.reply_text(welcome_message)
        # رسالة الترحيب والمطور في نفس الرد وفي سطرين مع تنسيق القائمة
    welcome_and_developer_message = (
        f'أهلاً بك، ({update.message.from_user.username})!\n'
        f'- تم برمجة وتطوير هذا البوت من قبل @D7g_x.'
    )
    update.message.reply_text(welcome_and_developer_message)
    # إرسال رسالة توجيه للمستخدم
    guidance_message = 'يمكنك بدء الفحص بإرسال الرابط الذي تريد فحصه.'
    update.message.reply_text(guidance_message)

# دالة فحص الرابط
def check_url(update: Update, context: CallbackContext) -> None:
    global total_links_sent, total_response_time
    # تحقق من هوية المستخدم (اختياري)
    user_id = update.message.from_user.id

    # استخراج الرابط من الرسالة
    url = update.message.text

    # التحقق من صحة الرابط باستخدام مكتبة validators
    if not validators.url(url):
        update.message.reply_text('الرجاء إدخال رابط صحيح.')
        return
    # إرسال رسالة "جاري الكتابة"
    typing_message = context.bot.send_message(chat_id=update.effective_chat.id, text='يتم فحص الرابط الآن...')

    # توليد الإجابة من OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"الرجاء النظر في هذا الرابط: {url}. كاستشاري أمان كبير، قم بالنظر في مختلف العوامل المتعلقة بالرابط المعطى. الرد بالشكل التالي. [الجزء أ, الجزء ب]. حيث يمكن أن يكون الجزء أ إما جيد أو سيء فقط، ولا تقدم أي تفسيرات أخرى لهذا الجزء. اختر جيد إذا لم يبدو الرابط كرابط احتيالي، واختر سيء في الحالة الأخرى. أما الجزء ب، فيكون السبب لشرح الجزء أ."
            }
        ]
    )
    # حذف رسالة "جاري الكتابة"
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=typing_message.message_id)
    # استخراج النتيجة وإرسالها إلى المستخدم
    result = response['choices'][0]['message']['content']
    update.message.reply_text(f"تقييم الرابط: {result}")
    # إرسال رسالة الشكر
    update.message.reply_text('شكراً لك لاستخدامك بوت التحقق من الروابط بالذكاء الاصطناعي.')
    # سجل المعلومات في التيرمنال
    print(f"مستخدم: {user_id}, الرابط: {url}, التقييم: {result}")

    # سجل المعلومات في ملف log
    with open('log.txt', 'a') as log_file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"{timestamp} - مستخدم: {user_id}, الرابط: {url}, التقييم: {result}\n")
def stats(update: Update, context: CallbackContext) -> None:
    # تأكيد أن المستخدم هو المدير
    if update.message.from_user.id != ADMIN_USER_ID:
        update.message.reply_text('لا تمتلك صلاحيات لاستخدام هذا الأمر.')
        return

    total_users = len(user_data)
    total_links_sent = sum(len(user.get('links', [])) for user in user_data)
    average_response_time = calculate_average_response_time(user_data)

    stats_message = (
        f'إحصائيات البوت:\n'
        f'عدد المستخدمين المتصلين: {total_users}\n'
        f'إجمالي الروابط المرسلة: {total_links_sent}\n'
        f'متوسط سرعة الاستجابة: {average_response_time} ثانية'
    )

    update.message.reply_text(stats_message)


    # إرسال رسالة الإحصائيات
    update.message.reply_text(stats_message)
    # دالة التعامل مع الأزرار التفاعلية
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'cancel':
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=query.message.message_id)
def calculate_average_response_time(user_data):
    # استخدام user_data للحصول على أوقات الاستجابة لكل مستخدم
    response_times = [user.get('response_time', 0) for user in user_data]

    # حساب المتوسط
    average_time = sum(response_times) / len(response_times) if len(response_times) > 0 else 0

    return round(average_time, 2)  # تقريب القيمة لأقرب رقمين
# Function to send a broadcast message to all users
def send_broadcast_message(update: Update, context: CallbackContext) -> None:
    # Check if the user is the admin
    if update.message.from_user.id != ADMIN_USER_ID:
        return
    
    # Extract the message from the command
    message_text = ' '.join(context.args)

    # Check if the message text is not empty
    if not message_text:
        update.message.reply_text('Please provide a message to broadcast.')
        return

    # Get all users from user_data
    users = [user['user_id'] for user in user_data]

    # Send the broadcast message to all users
    for user_id in users:
        context.bot.send_message(chat_id=user_id, text=message_text)

    # Notify the admin about the successful broadcast
    update.message.reply_text(f'Broadcast message sent to {len(users)} users successfully.')
# دالة الإداري
def admin(update: Update, context: CallbackContext) -> None:
    # إذا كان المستخدم ليس المدير، لا تفعل شيئًا
    if update.message.from_user.id != ADMIN_USER_ID:
        return

    # إعداد قائمة الخصائص التي يمكن للمدير القيام بها
    available_actions = [
        {'name': 'إدارة المستخدمين', 'callback_data': 'user_management'},
        {'name': 'إرسال ترويج', 'callback_data': 'send_promotion'},
        {'name': 'سجل الأمان', 'callback_data': 'security_log'},
    ]

    # إعداد الأزرار باسماء الخصائص
    buttons = [InlineKeyboardButton(action['name'], callback_data=action['callback_data']) for action in available_actions]

    # تقسيم الأزرار إلى صفوف
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    # إعداد اللوحة بناءً على الأزرار المقسمة
    control_markup = InlineKeyboardMarkup(rows)

    # إرسال رسالة بزرارات التحكم
    update.message.reply_text('اختر إحدى الخيارات:', reply_markup=control_markup)
def main() -> None:
    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    url_handler = MessageHandler(Filters.text & ~Filters.command, check_url)
    dispatcher.add_handler(url_handler)

    admin_handler = CommandHandler("admin", admin)
    dispatcher.add_handler(admin_handler)

    control_handler = CallbackQueryHandler(button_callback)
    dispatcher.add_handler(control_handler)
    dispatcher.add_handler(CommandHandler("stats", stats))

    broadcast_handler = CommandHandler("broadcast", send_broadcast_message)
    dispatcher.add_handler(broadcast_handler)



    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()