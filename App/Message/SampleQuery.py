from datetime import datetime


class SampleQuery:

    def __init__(self, sample_id):
        self.sample_id = sample_id

    def create_transaction(self):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        h_record = HeaderRec().to_string()
        m_record = ManufacturerRec(self.sample_id, current_time).to_string()
        l_record = TerminationRec().to_string()
        transaction = [h_record, m_record, l_record]
        return transaction


class HeaderRec:

    def __init__(self):
        pass

    def to_string(self):
        return "H|\^&"


class ManufacturerRec:

    def __init__(self, sample_id, target_time):
        self.rec_sample_id
        self.rec_target_time = target_time
        self.rec_label = "M"
        self.rec_seq = "1"
        self.rec_mrn = "101"
        self.rec_other = "0"

        self.m_record = (self.rec_label, self.rec_seq, self.mrn, self.rec_sample_id, self.rec_target_time, self.rec_other)

    def to_string(self):
        export_string = ""

        for field in self.m_record[:-1]:
            export_string = export_string + "|"

        export_string = export_string + self.m_record[-1]
        return export_string


class TerminationRec:

    def __init__(self):
        pass

    def to_string(self):
        return "L|1|N"
