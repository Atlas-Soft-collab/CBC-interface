
# CBC Interface

Interface بسيط بيستقبل نتائج تحاليل من جهاز Dymind CBC Analyzer عن طريق TCP/IP، ويحفظها محليًا، وممكن يبعتها لـ LIS.

## الجهاز
- Dymind (سلسلة DF)
- الاتصال: TCP/IP (مش RS-232)
- الجهاز هيبعت البيانات لـ IP:Port بتاعين البرنامج ده
- البروتوكول المتوقع: ASTM E1394 framing عبر TCP (لسه محتاج تأكيد من المانيول)

## الإعداد
1. `pip install -r requirements.txt`
2. عدّل `config/settings.json` بنفس الـ IP والـ Port المظبوطين على شاشة الجهاز (LIS Communication)
3. `python main.py`

## هيكل المشروع
```
cbc-interface/
├── main.py                 # نقطة الدخول
├── config/settings.json    # إعدادات IP/Port/Timeout
├── core/
│   ├── tcp_server.py       # بيسمع على البورت ويستقبل بيانات الجهاز
│   ├── protocol_parser.py  # بيفكك رسالة ASTM/HL7 لنتائج مفهومة
│   └── sample_handler.py   # بيربط Sample ID بالنتيجة
├── storage/database.py     # حفظ محلي بـ SQLite
├── ui/app_window.py        # واجهة بسيطة (اختياري)
├── logs/                   # سجل كل اتصال - مهم للـ debugging
└── tests/test_parser.py    # اختبار الـ parser على رسائل تجريبية
```

## الحالة الحالية
- [x] هيكل المشروع الأساسي
- [ ] تأكيد البروتوكول من المانيول (ASTM ولا HL7)
- [ ] تنفيذ tcp_server.py
- [ ] تنفيذ protocol_parser.py
- [ ] اختبار فعلي مع الجهاز
=======
# CBC-interface
interface for cbc analyzer

