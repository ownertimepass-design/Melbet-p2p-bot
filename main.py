import os
import io
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼 Get Banner", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("🤝 Become Affiliate Partner", callback_data="affiliate")],
    ]
    await update.message.reply_text(
        "🎯 *Welcome to Melbet BD Affiliate Bot!*\n\n"
        "Here you can:\n"
        "🖼 Get banners with promo codes\n"
        "❓ Ask any question.\n\n"
        "Choose an action below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "affiliate":
        await query.message.reply_text(
            "🤝 *Melbet Affiliate Program*\n\n"
            "Join and earn from every referral!\n\n"
            "👉 https://bit.ly/Official_melbetaffiliates\n\n"
            "📞 Manager: @Melbet_BdManager",
            parse_mode="Markdown"
        )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    cat = data.get("category", "sport")
    promo = data.get("promo", "").upper().strip()
    lang = data.get("lang", "bn")

    await update.message.reply_text("⏳ ব্যানার তৈরি হচ্ছে... একটু অপেক্ষা করুন")

    try:
        zip_buffer = create_zip(cat, promo, lang)
        fname = f"Melbet_{cat}_Banners{'_'+promo if promo else ''}.zip"
        caption = (
            f"✅ *Melbet Banners Ready!*\n\n"
            f"📁 Category: {cat.upper()}\n"
            f"{'🎫 Promo Code: `' + promo + '`' if promo else ''}  \n\n"
            f"📞 Support: @Melbet\\_BdManager"
        )
        await update.message.reply_document(
            document=zip_buffer,
            filename=fname,
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ─── Banner configs ───────────────────────────────────────
BANNERS = {
    "sport": [
        {"bg1":"#0a1628","bg2":"#1e3a5f","acc":"#FFC323","title":"SPORTS BET","sub_bn":"সেরা অডস পান","sub_en":"Best Odds","tag":"LIVE"},
        {"bg1":"#0a2010","bg2":"#1a4a28","acc":"#00e676","title":"FOOTBALL","sub_bn":"বড় জিতুন","sub_en":"Win Big","tag":"HOT"},
        {"bg1":"#2a0030","bg2":"#5c0060","acc":"#e040fb","title":"TENNIS","sub_bn":"গ্র্যান্ড স্লাম","sub_en":"Grand Slam","tag":"NEW"},
        {"bg1":"#1a1a00","bg2":"#3a3000","acc":"#ffd740","title":"BASKETBALL","sub_bn":"NBA অডস","sub_en":"NBA Odds","tag":"VIP"},
    ],
    "bonus": [
        {"bg1":"#3a0a00","bg2":"#6e1800","acc":"#FFC323","title":"175% BONUS","sub_bn":"ওয়েলকাম অফার","sub_en":"Welcome Offer","tag":"NEW"},
        {"bg1":"#001a3e","bg2":"#002e6e","acc":"#40c4ff","title":"FREE BET","sub_bn":"ডিপোজিট ছাড়া","sub_en":"No Deposit","tag":"HOT"},
        {"bg1":"#3a0020","bg2":"#6e0040","acc":"#FFC323","title":"CASHBACK","sub_bn":"প্রতি সপ্তাহে","sub_en":"Every Week","tag":"VIP"},
        {"bg1":"#003a00","bg2":"#006e00","acc":"#69f0ae","title":"VIP BONUS","sub_bn":"এক্সক্লুসিভ","sub_en":"Exclusive","tag":"VIP"},
    ],
    "casino": [
        {"bg1":"#2a003a","bg2":"#5c0060","acc":"#e040fb","title":"CASINO","sub_bn":"লাইভ গেমস","sub_en":"Live Games","tag":"LIVE"},
        {"bg1":"#3a1a00","bg2":"#6e3000","acc":"#ff9100","title":"SLOTS","sub_bn":"জ্যাকপট","sub_en":"Win Jackpot","tag":"HOT"},
        {"bg1":"#001a3a","bg2":"#002a6e","acc":"#40c4ff","title":"ROULETTE","sub_bn":"লাইভ টেবিল","sub_en":"Live Table","tag":"LIVE"},
        {"bg1":"#1a1a00","bg2":"#3a3800","acc":"#ffd740","title":"BLACKJACK","sub_bn":"VIP টেবিল","sub_en":"VIP Table","tag":"VIP"},
    ],
    "esport": [
        {"bg1":"#001a3a","bg2":"#002a6e","acc":"#40c4ff","title":"E-SPORT","sub_bn":"লাইভ বেটিং","sub_en":"Live Betting","tag":"LIVE"},
        {"bg1":"#2a003a","bg2":"#4a006e","acc":"#b388ff","title":"GAMING","sub_bn":"টুর্নামেন্ট","sub_en":"Tournament","tag":"HOT"},
        {"bg1":"#003a2a","bg2":"#006e4a","acc":"#64ffda","title":"CS2 & DOTA","sub_bn":"eSports বেট","sub_en":"Esports Bet","tag":"NEW"},
        {"bg1":"#3a1a00","bg2":"#6e3a00","acc":"#ffd740","title":"MOBILE","sub_bn":"গেমিং বেট","sub_en":"Gaming Bet","tag":"HOT"},
    ],
    "epl": [
        {"bg1":"#3a0000","bg2":"#6e0000","acc":"#FFC323","title":"PREMIER LEAGUE","sub_bn":"২০২৪/২৫ সিজন","sub_en":"2024/25 Season","tag":"HOT"},
        {"bg1":"#001a3a","bg2":"#002a6e","acc":"#40c4ff","title":"EPL ODDS","sub_bn":"ম্যাচওয়িক","sub_en":"Matchweek","tag":"LIVE"},
        {"bg1":"#003a1a","bg2":"#006e30","acc":"#69f0ae","title":"EPL WIN","sub_bn":"সেরা মূল্য","sub_en":"Best Price","tag":"VIP"},
        {"bg1":"#2a2a00","bg2":"#4a4400","acc":"#ffd740","title":"TOP 4 RACE","sub_bn":"লাইভ অডস","sub_en":"Live Odds","tag":"NEW"},
    ],
    "champions": [
        {"bg1":"#00003a","bg2":"#00006e","acc":"#536dfe","title":"CHAMPIONS","sub_bn":"লিগ UCL","sub_en":"League UCL","tag":"UCL"},
        {"bg1":"#2a2a00","bg2":"#4a4400","acc":"#ffd740","title":"UEFA CL","sub_bn":"গ্রুপ স্টেজ","sub_en":"Group Stage","tag":"HOT"},
        {"bg1":"#003a1a","bg2":"#006e30","acc":"#69f0ae","title":"UCL 2025","sub_bn":"নকআউট","sub_en":"Knockout","tag":"LIVE"},
        {"bg1":"#3a1a00","bg2":"#6e3000","acc":"#ff9100","title":"UCL FINAL","sub_bn":"চ্যাম্পিয়নস","sub_en":"Champions","tag":"VIP"},
    ],
    "cricket": [
        {"bg1":"#003a1a","bg2":"#006e30","acc":"#69f0ae","title":"CRICKET","sub_bn":"লাইভ ম্যাচ","sub_en":"Live Match","tag":"LIVE"},
        {"bg1":"#001a3a","bg2":"#002a6e","acc":"#40c4ff","title":"T20 WORLD","sub_bn":"বিশ্বকাপ","sub_en":"World Cup","tag":"HOT"},
        {"bg1":"#3a1a00","bg2":"#6e3000","acc":"#FFC323","title":"TEST MATCH","sub_bn":"ক্রিকেট বেট","sub_en":"Cricket Bet","tag":"LIVE"},
        {"bg1":"#2a003a","bg2":"#5c006e","acc":"#e040fb","title":"IPL & BPL","sub_bn":"সেরা অডস","sub_en":"Best Odds","tag":"HOT"},
    ],
    "ipl": [
        {"bg1":"#3a1a00","bg2":"#6e2800","acc":"#FFC323","title":"IPL 2025","sub_bn":"ভারত সেরা বেট","sub_en":"India Best Bet","tag":"HOT"},
        {"bg1":"#001a3a","bg2":"#002a6e","acc":"#40c4ff","title":"IPL LIVE","sub_bn":"এখনই বেট","sub_en":"Bet Now","tag":"LIVE"},
        {"bg1":"#003a1a","bg2":"#005c28","acc":"#69f0ae","title":"IPL FINAL","sub_bn":"বড় জিতুন","sub_en":"Win Big","tag":"VIP"},
        {"bg1":"#2a2a00","bg2":"#4a4000","acc":"#ffd740","title":"IPL ODDS","sub_bn":"সেরা মূল্য","sub_en":"Top Price","tag":"NEW"},
    ],
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_zip(category, promo, lang):
    configs = BANNERS.get(category, BANNERS["sport"])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, cfg in enumerate(configs):
            img = draw_banner(cfg, promo, lang)
            ib = io.BytesIO()
            img.save(ib, 'PNG')
            ib.seek(0)
            zf.writestr(f"Melbet_Banner_{i+1}{'_'+promo if promo else ''}.png", ib.getvalue())
    buf.seek(0)
    return buf

def draw_banner(cfg, promo, lang):
    W, H = 1080, 1080
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)

    # Gradient background
    c1 = hex_to_rgb(cfg['bg1'])
    c2 = hex_to_rgb(cfg['bg2'])
    for y in range(H):
        r = int(c1[0]+(c2[0]-c1[0])*y/H)
        g = int(c1[1]+(c2[1]-c1[1])*y/H)
        b = int(c1[2]+(c2[2]-c1[2])*y/H)
        draw.line([(0,y),(W,y)], fill=(r,g,b))

    # Glow circle top-right
    acc = hex_to_rgb(cfg['acc'])
    glow = Image.new('RGBA', (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for radius in range(300, 0, -10):
        alpha = int(60 * (1 - radius/300))
        gd.ellipse([W-radius-100, -radius//2, W+radius-100, radius*3//2],
                   fill=(*acc, alpha))
    img.paste(Image.fromarray(img.__array__()), (0,0))
    try:
        img = Image.alpha_composite(img.convert('RGBA'), glow).convert('RGB')
        draw = ImageDraw.Draw(img)
    except:
        draw = ImageDraw.Draw(img)

    # Grid lines
    for x in range(0, W, 60):
        draw.line([(x,0),(x,H)], fill=(255,255,255,10), width=1)
    for y in range(0, H, 60):
        draw.line([(0,y),(W,y)], fill=(255,255,255,10), width=1)

    # Top stripe
    draw.rectangle([0,0,W,10], fill='#FFC323')

    # Load fonts
    try:
        f_logo  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        f_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
        f_sub   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        f_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        f_tag   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        f_plbl  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        f_pcode = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
    except:
        f_logo = f_title = f_sub = f_small = f_tag = f_plbl = f_pcode = ImageFont.load_default()

    # MELBET logo
    draw.text((40, 26), "M", font=f_logo, fill='#FFC323')
    m_w = draw.textlength("M", font=f_logo)
    draw.text((40+m_w+4, 26), "ELBET", font=f_logo, fill='#FFFFFF')

    # TAG pill
    tag = cfg.get('tag','HOT')
    tag_w = int(draw.textlength(tag, font=f_tag)) + 40
    tx, ty = W-tag_w-30, 26
    draw.rounded_rectangle([tx, ty, tx+tag_w, ty+44], radius=10, fill=cfg['acc'])
    draw.text((tx+tag_w//2, ty+22), tag, font=f_tag, fill='#111111', anchor='mm')

    # Big decorative shape center
    draw.ellipse([W//2-220, H//2-220, W//2+220, H//2+220],
                 fill=(*acc, 18) if len(acc)==3 else acc)
    draw.ellipse([W//2-160, H//2-160, W//2+160, H//2+160],
                 outline=cfg['acc'], width=3)

    # Title
    title = cfg['title']
    tw = draw.textlength(title, font=f_title)
    draw.text(((W-tw)//2, int(H*0.17)), title, font=f_title, fill='#FFFFFF')

    # Accent underline
    draw.rectangle([(W-tw)//2, int(H*0.17)+118, (W+tw)//2, int(H*0.17)+124], fill=cfg['acc'])

    # Sub text
    sub = cfg.get('sub_bn' if lang=='bn' else 'sub_en', '')
    sub2 = cfg.get('sub_en','')
    sw = draw.textlength(sub, font=f_sub)
    draw.text(((W-sw)//2, int(H*0.33)), sub, font=f_sub, fill=cfg['acc'])
    sw2 = draw.textlength(sub2, font=f_small)
    draw.text(((W-sw2)//2, int(H*0.42)), sub2, font=f_small, fill=(255,255,255,140))

    # Divider
    draw.rectangle([W//2-80, int(H*0.48), W//2+80, int(H*0.48)+2], fill=cfg['acc'])

    # PROMO CODE box
    if promo:
        bw, bh = 680, 120
        bx, by = (W-bw)//2, H-200
        # Shadow
        draw.rounded_rectangle([bx+6, by+6, bx+bw+6, by+bh+6], radius=18, fill=(0,0,0,80))
        # White box
        draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=18, fill='#FFFFFF')
        # Shine
        draw.rounded_rectangle([bx, by, bx+bw, by+bh//2], radius=18, fill=(255,255,255,200))
        # Label
        lw = draw.textlength("PROMO CODE:", font=f_plbl)
        draw.text(((W-lw)//2, by+22), "PROMO CODE:", font=f_plbl, fill='#666666')
        # Code
        cw = draw.textlength(promo, font=f_pcode)
        draw.text(((W-cw)//2, by+60), promo, font=f_pcode, fill='#FFC323')
    else:
        ww = draw.textlength("melbet.com", font=f_small)
        draw.text(((W-ww)//2, H-60), "melbet.com", font=f_small, fill=(255,255,255,60))

    # Bottom stripe
    draw.rectangle([0, H-10, W, H], fill='#FFC323')

    return img

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    print("✅ Melbet Bot running...")
    app.run_polling(drop_pending_updates=True)
