import json, os, uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# =============================================
# ⚙️ غيّر هذا فقط
# =============================================
BOT_TOKEN = "8762550447:AAFYl5P2KitqHTG5VAcD8MUEI4xmL9MgWXM"
ADMIN_ID   = 7903475836   # ID تيليجرامك

DATA_FILE  = "data.json"

# =============================================
# 💾 البيانات
# =============================================
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}, "offers": [], "messages": []}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

# =============================================
# 🏠 START
# =============================================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    data = load()
    kb = []
    for cid, cat in data["categories"].items():
        kb.append([InlineKeyboardButton(f"📂 {cat['name']}", callback_data=f"CAT|{cid}")])
    if data["offers"]:
        kb.append([InlineKeyboardButton("🔥 العروض", callback_data="OFFERS")])
    kb.append([InlineKeyboardButton("💬 تواصل مع المطور", callback_data="CONTACT")])

    # زر الإدارة للأدمن فقط
    if is_admin(update):
        kb.append([InlineKeyboardButton("⚙️ لوحة الإدارة", callback_data="ADMIN")])

    await update.effective_message.reply_text(
        "🛒 *أهلاً بك في المتجر!*\nاختر من القائمة:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# =============================================
# 📂 عرض قسم
# =============================================
async def show_cat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cid = q.data.split("|")[1]
    data = load()
    cat = data["categories"].get(cid)
    if not cat:
        await q.edit_message_text("❌ القسم غير موجود"); return

    kb = []
    for i, item in enumerate(cat.get("items", [])):
        kb.append([InlineKeyboardButton(f"▸ {item['name']}", callback_data=f"ITEM|{cid}|{i}")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="HOME")])

    await q.edit_message_text(
        f"📂 *{cat['name']}*\n{cat.get('desc','')}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb)
    )

# =============================================
# 📄 عرض عنصر
# =============================================
async def show_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, cid, idx = q.data.split("|")
    data = load()
    item = data["categories"][cid]["items"][int(idx)]
    kb = [[InlineKeyboardButton("🔙 رجوع للقسم", callback_data=f"CAT|{cid}")]]

    text = f"*{item['name']}*\n\n{item.get('content','')}"
    if item.get("price"):
        text += f"\n\n💰 *{item['price']}*"

    if item.get("photo"):
        await q.message.reply_photo(item["photo"], caption=text, parse_mode="Markdown",
                                     reply_markup=InlineKeyboardMarkup(kb))
        await q.delete_message()
    elif item.get("file"):
        await q.message.reply_document(item["file"], caption=text, parse_mode="Markdown",
                                        reply_markup=InlineKeyboardMarkup(kb))
        await q.delete_message()
    else:
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# =============================================
# 🔥 العروض
# =============================================
async def show_offers(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    data = load()
    kb = [[InlineKeyboardButton("🔙 رجوع", callback_data="HOME")]]
    if not data["offers"]:
        await q.edit_message_text("لا توجد عروض حالياً", reply_markup=InlineKeyboardMarkup(kb)); return
    text = "🔥 *العروض الخاصة:*\n\n"
    for o in data["offers"]:
        text += f"🏷️ *{o['title']}*\n{o['desc']}\n\n"
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# =============================================
# 💬 تواصل
# =============================================
async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data["state"] = "CONTACT"
    kb = [[InlineKeyboardButton("🔙 إلغاء", callback_data="HOME")]]
    await q.edit_message_text("💬 اكتب رسالتك وسيتواصل معك المطور:", reply_markup=InlineKeyboardMarkup(kb))

# =============================================
# 🏠 رجوع للرئيسية
# =============================================
async def go_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data.clear()
    data = load()
    kb = []
    for cid, cat in data["categories"].items():
        kb.append([InlineKeyboardButton(f"📂 {cat['name']}", callback_data=f"CAT|{cid}")])
    if data["offers"]:
        kb.append([InlineKeyboardButton("🔥 العروض", callback_data="OFFERS")])
    kb.append([InlineKeyboardButton("💬 تواصل مع المطور", callback_data="CONTACT")])
    if update.effective_user.id == ADMIN_ID:
        kb.append([InlineKeyboardButton("⚙️ لوحة الإدارة", callback_data="ADMIN")])
    await q.edit_message_text("🛒 *أهلاً بك في المتجر!*\nاختر من القائمة:",
                               parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# =============================================
# ⚙️ لوحة الإدارة
# =============================================
async def admin_panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    ctx.user_data.clear()

    kb = [
        [InlineKeyboardButton("📂 الأقسام", callback_data="ADMIN_CATS"),
         InlineKeyboardButton("🔥 العروض", callback_data="ADMIN_OFFERS")],
        [InlineKeyboardButton("📩 رسائل العملاء", callback_data="ADMIN_MSGS")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="HOME")]
    ]
    await q.edit_message_text("⚙️ *لوحة الإدارة*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

# --- إدارة الأقسام ---
async def admin_cats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    data = load()

    kb = []
    for cid, cat in data["categories"].items():
        kb.append([
            InlineKeyboardButton(f"📂 {cat['name']}", callback_data=f"ADMIN_CAT_ITEMS|{cid}"),
            InlineKeyboardButton("🗑", callback_data=f"ADMIN_DEL_CAT|{cid}")
        ])
    kb.append([InlineKeyboardButton("➕ قسم جديد", callback_data="ADMIN_ADD_CAT")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="ADMIN")])

    await q.edit_message_text("📂 *إدارة الأقسام:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

async def admin_add_cat_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    ctx.user_data["state"] = "ADD_CAT_NAME"
    kb = [[InlineKeyboardButton("🔙 إلغاء", callback_data="ADMIN_CATS")]]
    await q.edit_message_text("📂 اكتب *اسم القسم الجديد:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

async def admin_del_cat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    cid = q.data.split("|")[1]
    data = load()
    name = data["categories"].get(cid, {}).get("name", "")
    del data["categories"][cid]
    save(data)
    await q.answer(f"✅ تم حذف '{name}'", show_alert=True)
    # أعد عرض الأقسام
    kb = []
    for c, cat in data["categories"].items():
        kb.append([
            InlineKeyboardButton(f"📂 {cat['name']}", callback_data=f"ADMIN_CAT_ITEMS|{c}"),
            InlineKeyboardButton("🗑", callback_data=f"ADMIN_DEL_CAT|{c}")
        ])
    kb.append([InlineKeyboardButton("➕ قسم جديد", callback_data="ADMIN_ADD_CAT")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="ADMIN")])
    await q.edit_message_text("📂 *إدارة الأقسام:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

# --- إدارة عناصر القسم ---
async def admin_cat_items(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    cid = q.data.split("|")[1]
    ctx.user_data["current_cat"] = cid
    data = load()
    cat = data["categories"][cid]

    kb = []
    for i, item in enumerate(cat.get("items", [])):
        kb.append([
            InlineKeyboardButton(f"▸ {item['name']}", callback_data=f"ITEM|{cid}|{i}"),
            InlineKeyboardButton("🗑", callback_data=f"ADMIN_DEL_ITEM|{cid}|{i}")
        ])
    kb.append([InlineKeyboardButton("➕ إضافة عنصر", callback_data=f"ADMIN_ADD_ITEM|{cid}")])
    kb.append([InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="ADMIN_CATS")])

    await q.edit_message_text(
        f"📂 *{cat['name']}* — العناصر:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb)
    )

async def admin_add_item_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    cid = q.data.split("|")[1]
    ctx.user_data["state"] = "ADD_ITEM_NAME"
    ctx.user_data["current_cat"] = cid
    kb = [[InlineKeyboardButton("🔙 إلغاء", callback_data=f"ADMIN_CAT_ITEMS|{cid}")]]
    await q.edit_message_text("📄 اكتب *اسم العنصر:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

async def admin_del_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    _, cid, idx = q.data.split("|")
    data = load()
    removed = data["categories"][cid]["items"].pop(int(idx))
    save(data)
    cat = data["categories"][cid]
    kb = []
    for i, item in enumerate(cat.get("items", [])):
        kb.append([
            InlineKeyboardButton(f"▸ {item['name']}", callback_data=f"ITEM|{cid}|{i}"),
            InlineKeyboardButton("🗑", callback_data=f"ADMIN_DEL_ITEM|{cid}|{i}")
        ])
    kb.append([InlineKeyboardButton("➕ إضافة عنصر", callback_data=f"ADMIN_ADD_ITEM|{cid}")])
    kb.append([InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="ADMIN_CATS")])
    await q.answer(f"✅ تم حذف '{removed['name']}'", show_alert=True)
    await q.edit_message_text(f"📂 *{cat['name']}* — العناصر:", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

# --- إدارة العروض ---
async def admin_offers(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    data = load()
    kb = []
    for i, o in enumerate(data["offers"]):
        kb.append([
            InlineKeyboardButton(f"🏷 {o['title']}", callback_data=f"NOOP"),
            InlineKeyboardButton("🗑", callback_data=f"ADMIN_DEL_OFFER|{i}")
        ])
    kb.append([InlineKeyboardButton("➕ عرض جديد", callback_data="ADMIN_ADD_OFFER")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="ADMIN")])
    await q.edit_message_text("🔥 *إدارة العروض:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

async def admin_add_offer_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    ctx.user_data["state"] = "ADD_OFFER_TITLE"
    kb = [[InlineKeyboardButton("🔙 إلغاء", callback_data="ADMIN_OFFERS")]]
    await q.edit_message_text("🔥 اكتب *عنوان العرض:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

async def admin_del_offer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    idx = int(q.data.split("|")[1])
    data = load()
    removed = data["offers"].pop(idx)
    save(data)
    kb = []
    for i, o in enumerate(data["offers"]):
        kb.append([
            InlineKeyboardButton(f"🏷 {o['title']}", callback_data="NOOP"),
            InlineKeyboardButton("🗑", callback_data=f"ADMIN_DEL_OFFER|{i}")
        ])
    kb.append([InlineKeyboardButton("➕ عرض جديد", callback_data="ADMIN_ADD_OFFER")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="ADMIN")])
    await q.answer(f"✅ تم حذف '{removed['title']}'", show_alert=True)
    await q.edit_message_text("🔥 *إدارة العروض:*", parse_mode="Markdown",
                               reply_markup=InlineKeyboardMarkup(kb))

# --- رسائل العملاء ---
async def admin_msgs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    data = load()
    msgs = data.get("messages", [])
    kb = []
    for i, m in enumerate(msgs):
        kb.append([InlineKeyboardButton(
            f"👤 {m['name']}: {m['msg'][:25]}...",
            callback_data=f"ADMIN_REPLY|{i}"
        )])
    kb.append([InlineKeyboardButton("🗑 مسح الكل", callback_data="ADMIN_CLEAR_MSGS")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="ADMIN")])
    text = f"📩 *رسائل العملاء* ({len(msgs)}):" if msgs else "📭 لا توجد رسائل"
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def admin_reply_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    idx = int(q.data.split("|")[1])
    data = load()
    m = data["messages"][idx]
    ctx.user_data["state"] = "REPLY_MSG"
    ctx.user_data["reply_to"] = m["user_id"]
    ctx.user_data["reply_idx"] = idx
    kb = [[InlineKeyboardButton("🔙 إلغاء", callback_data="ADMIN_MSGS")]]
    await q.edit_message_text(
        f"📩 *رسالة من {m['name']}:*\n{m['msg']}\n\nاكتب ردك:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb)
    )

async def admin_clear_msgs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(update): return
    data = load()
    data["messages"] = []
    save(data)
    kb = [[InlineKeyboardButton("🔙 رجوع", callback_data="ADMIN")]]
    await q.edit_message_text("✅ تم مسح جميع الرسائل", reply_markup=InlineKeyboardMarkup(kb))

# =============================================
# ✍️ معالج النصوص (الحالات)
# =============================================
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    state = ctx.user_data.get("state")
    text = update.message.text
    data = load()

    # -- عميل: إرسال رسالة --
    if state == "CONTACT":
        user = update.effective_user
        data["messages"].append({
            "user_id": user.id,
            "name": user.full_name,
            "username": user.username or "",
            "msg": text
        })
        save(data)
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 *رسالة جديدة!*\n👤 {user.full_name} | @{user.username or '-'} | `{user.id}`\n\n{text}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ تم إرسال رسالتك! سيتواصل معك المطور قريباً.")
        ctx.user_data.clear()

    # -- أدمن: رد على عميل --
    elif state == "REPLY_MSG" and is_admin(update):
        uid = ctx.user_data["reply_to"]
        await ctx.bot.send_message(chat_id=uid, text=f"📨 *رسالة من المطور:*\n\n{text}", parse_mode="Markdown")
        await update.message.reply_text("✅ تم إرسال الرد!")
        ctx.user_data.clear()

    # -- أدمن: إضافة قسم --
    elif state == "ADD_CAT_NAME" and is_admin(update):
        ctx.user_data["cat_name"] = text
        ctx.user_data["state"] = "ADD_CAT_DESC"
        await update.message.reply_text("📝 اكتب *وصف القسم* (أو أرسل - للتخطي):", parse_mode="Markdown")

    elif state == "ADD_CAT_DESC" and is_admin(update):
        cid = str(uuid.uuid4())[:8]
        data["categories"][cid] = {
            "name": ctx.user_data["cat_name"],
            "desc": "" if text == "-" else text,
            "items": []
        }
        save(data)
        await update.message.reply_text(f"✅ تم إضافة قسم *{ctx.user_data['cat_name']}*", parse_mode="Markdown")
        ctx.user_data.clear()

    # -- أدمن: إضافة عنصر --
    elif state == "ADD_ITEM_NAME" and is_admin(update):
        ctx.user_data["item_name"] = text
        ctx.user_data["state"] = "ADD_ITEM_CONTENT"
        await update.message.reply_text("📝 اكتب *محتوى/وصف العنصر:*", parse_mode="Markdown")

    elif state == "ADD_ITEM_CONTENT" and is_admin(update):
        ctx.user_data["item_content"] = text
        ctx.user_data["state"] = "ADD_ITEM_PRICE"
        await update.message.reply_text("💰 اكتب *السعر* (أو أرسل - إذا لا يوجد):", parse_mode="Markdown")

    elif state == "ADD_ITEM_PRICE" and is_admin(update):
        ctx.user_data["item_price"] = "" if text == "-" else text
        ctx.user_data["state"] = "ADD_ITEM_MEDIA"
        await update.message.reply_text("🖼 أرسل *صورة أو ملف* للعنصر (أو أرسل - للتخطي):", parse_mode="Markdown")

    elif state == "ADD_ITEM_MEDIA" and is_admin(update) and text == "-":
        _save_item(data, ctx, photo=None, file_id=None)
        await update.message.reply_text(f"✅ تم إضافة *{ctx.user_data.get('item_name','')}*", parse_mode="Markdown")
        ctx.user_data.clear()

    # -- أدمن: إضافة عرض --
    elif state == "ADD_OFFER_TITLE" and is_admin(update):
        ctx.user_data["offer_title"] = text
        ctx.user_data["state"] = "ADD_OFFER_DESC"
        await update.message.reply_text("📝 اكتب *تفاصيل العرض:*", parse_mode="Markdown")

    elif state == "ADD_OFFER_DESC" and is_admin(update):
        data["offers"].append({"title": ctx.user_data["offer_title"], "desc": text})
        save(data)
        await update.message.reply_text(f"✅ تم إضافة العرض *{ctx.user_data['offer_title']}*", parse_mode="Markdown")
        ctx.user_data.clear()

# =============================================
# 🖼 معالج الصور والملفات (للأدمن)
# =============================================
async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.user_data.get("state") != "ADD_ITEM_MEDIA" or not is_admin(update): return
    photo_id = update.message.photo[-1].file_id
    data = load()
    _save_item(data, ctx, photo=photo_id, file_id=None)
    await update.message.reply_text(f"✅ تم إضافة *{ctx.user_data.get('item_name','')}* مع صورة", parse_mode="Markdown")
    ctx.user_data.clear()

async def handle_file(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.user_data.get("state") != "ADD_ITEM_MEDIA" or not is_admin(update): return
    file_id = update.message.document.file_id
    data = load()
    _save_item(data, ctx, photo=None, file_id=file_id)
    await update.message.reply_text(f"✅ تم إضافة *{ctx.user_data.get('item_name','')}* مع ملف", parse_mode="Markdown")
    ctx.user_data.clear()

def _save_item(data, ctx, photo, file_id):
    cid = ctx.user_data["current_cat"]
    data["categories"][cid]["items"].append({
        "name":    ctx.user_data.get("item_name", ""),
        "content": ctx.user_data.get("item_content", ""),
        "price":   ctx.user_data.get("item_price", ""),
        "photo":   photo,
        "file":    file_id
    })
    save(data)

# =============================================
# ▶️ تشغيل
# =============================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(go_home,             pattern="^HOME$"))
    app.add_handler(CallbackQueryHandler(show_cat,            pattern="^CAT\|"))
    app.add_handler(CallbackQueryHandler(show_item,           pattern="^ITEM\|"))
    app.add_handler(CallbackQueryHandler(show_offers,         pattern="^OFFERS$"))
    app.add_handler(CallbackQueryHandler(contact,             pattern="^CONTACT$"))
    app.add_handler(CallbackQueryHandler(admin_panel,         pattern="^ADMIN$"))
    app.add_handler(CallbackQueryHandler(admin_cats,          pattern="^ADMIN_CATS$"))
    app.add_handler(CallbackQueryHandler(admin_add_cat_start, pattern="^ADMIN_ADD_CAT$"))
    app.add_handler(CallbackQueryHandler(admin_del_cat,       pattern="^ADMIN_DEL_CAT\|"))
    app.add_handler(CallbackQueryHandler(admin_cat_items,     pattern="^ADMIN_CAT_ITEMS\|"))
    app.add_handler(CallbackQueryHandler(admin_add_item_start,pattern="^ADMIN_ADD_ITEM\|"))
    app.add_handler(CallbackQueryHandler(admin_del_item,      pattern="^ADMIN_DEL_ITEM\|"))
    app.add_handler(CallbackQueryHandler(admin_offers,        pattern="^ADMIN_OFFERS$"))
    app.add_handler(CallbackQueryHandler(admin_add_offer_start,pattern="^ADMIN_ADD_OFFER$"))
    app.add_handler(CallbackQueryHandler(admin_del_offer,     pattern="^ADMIN_DEL_OFFER\|"))
    app.add_handler(CallbackQueryHandler(admin_msgs,          pattern="^ADMIN_MSGS$"))
    app.add_handler(CallbackQueryHandler(admin_reply_start,   pattern="^ADMIN_REPLY\|"))
    app.add_handler(CallbackQueryHandler(admin_clear_msgs,    pattern="^ADMIN_CLEAR_MSGS$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.answer(), pattern="^NOOP$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
