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
    Ointment = "OINTMENT", "Ointment"
    Lotion = "LOTION", "Lotion"
    B_Cream = "B/CREAM", "B/Cream"
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
            cls.Ointment,
            cls.Lotion,
            cls.B_Cream,
            cls.OTH,
        )
