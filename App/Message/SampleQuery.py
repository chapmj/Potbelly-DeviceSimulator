from datetime import datetime


class SampleQuery:

    def __init__(self, sample_id):
        self.sample_id = sample_id

    def create_transaction(self):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        h_record = "H|\^&"
        m_record = "M|1|101|" + self.sample_id + "|" + current_time + "|0"
        l_record = "L|1|N"
        transaction = [h_record, m_record, l_record]
        return transaction
