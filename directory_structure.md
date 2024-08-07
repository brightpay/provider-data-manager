provider-data-manager/
│
├── src/
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── practitioner_processor.py
│   │   ├── practice_processor.py
│   │   └── common/
│   │       ├── __init__.py
│   │       ├── base_processor.py  # Base class for processors
│   │       └── utils.py           # Utility functions for processors
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── practitioner.py
│   │   ├── practice.py
│   │   ├── education.py
│   │   ├── membership.py
│   │   ├── award.py
│   │   ├── clinical_interest.py
│   │   ├── condition_treated.py
│   │   ├── opening_hours.py
│   │   ├── schedule.py
│   │   ├── service_pricing.py
│   │   └── photo.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── practitioner_service.py
│   │   ├── practice_service.py
│   │   ├── education_service.py
│   │   ├── membership_service.py
│   │   ├── award_service.py
│   │   ├── clinical_interest_service.py
│   │   ├── condition_treated_service.py
│   │   ├── opening_hours_service.py
│   │   ├── schedule_service.py
│   │   ├── service_pricing_service.py
│   │   └── photo_service.py
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── practitioner_handler.py
│   │   ├── practice_handler.py
│   │   ├── education_handler.py
│   │   ├── membership_handler.py
│   │   ├── award_handler.py
│   │   ├── clinical_interest_handler.py
│   │   ├── condition_treated_handler.py
│   │   ├── opening_hours_handler.py
│   │   ├── schedule_handler.py
│   │   ├── service_pricing_handler.py
│   │   └── photo_handler.py
│   │
│   ├── __init__.py
│   ├── app.py                       # Main entry point
│   └── config.py                    # Configuration settings
│
├── tests/
│   ├── processors/
│   ├── models/
│   ├── services/
│   ├── handlers/
│   └── __init__.py
│
├── requirements.txt
├── README.md
└── template.yaml                    # SAM or CloudFormation template
