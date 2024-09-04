class Practice:
    def __init__(self, provider_id, practice):
        self.provider_id = provider_id
        self.practice_data = practice
        self.provider_columns = ['provider_id','slug','name','thumbnail','type','subtype','country','state','city','brighthealth_ssr']
        self.practice_columns = ['provider_id','name','name_ext','type','subtype','lat','lng','address','pincode','locality','sublocality','route','city','state','country','open_24x7','specialty','multispecialty','recommendations','rating','website','logo_url','cover_photo_url','summary','min_consultation_fee','max_consultation_fee','formatted_phone','phone','email']
        self.provider_meta_id_mapping_columns = ['provider_id','practo_id','google_place_id','justdial_doc_id','nmc_doctor_id','sdc_reg_num','abha_id','health_system_practitioner_id','health_system_practice_id','health_system_city_id','health_system_specialty_id']

    def __repr__(self):
        return f"Practice({self.provider_id}, {self.practice_data})"
    
    def process_data(self):
        provider_record = {}
        practice_record = {}
        practice_additional_data = {}
        provider_meta_id_mappings = {}
        for _column in self.practice_data.keys():
            if _column in self.provider_columns:
                provider_record[_column] = self.practice_data[_column]
            if _column in self.practice_columns:
                provider_record[_column] = self.practice_data[_column]
            else:
                practice_additional_data[_column] = self.practice_data[_column]
            if _column in self.provider_meta_id_mapping_columns:
                provider_meta_id_mappings[_column] = self.practice_data[_column]
        return {
            "provider": provider_record,
            "practice": practice_record,
            "practice_extra": practice_additional_data,
            "meta_mappings": provider_meta_id_mappings
        }
