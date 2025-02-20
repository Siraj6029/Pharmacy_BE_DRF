class ProductTypeChoices:
    TAB = "TAB", "Tablets"
    SYP = "SYP", "Syrup"
    CREAM = "CREAM", "Cream"
    CAP = "CAP", "Capsule"
    INJ = "INJ", "Injection"
    DROPS = "DROPS", "Drops"
    DRIP = "DRIP", "Drips"
    SECHET = "SECHET", "Sechet"
    SAOP = "SAOP", "Saop"
    TP = "T/PASTE", "T/Paste"
    OINTMENT = "OINTMENT", "Ointment"
    LOTION = "LOTION", "Lotion"
    B_CREAM = "B/CREAM", "B/Cream"
    INHALER = "INHALER", "INHALER"
    OTH = "OTH", "Others"

    @classmethod
    def get_choices(cls):
        return (
            cls.TAB,
            cls.SYP,
            cls.CREAM,
            cls.CAP,
            cls.INJ,
            cls.DROPS,
            cls.DRIP,
            cls.SECHET,
            cls.SAOP,
            cls.TP,
            cls.OINTMENT,
            cls.LOTION,
            cls.B_CREAM,
            cls.INHALER,
            cls.OTH,
        )
