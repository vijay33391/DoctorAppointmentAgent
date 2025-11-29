import pandas as pd
from typing_extensions import Literal, Annotated
from langchain_core.tools import tool
from models_validator.validator import DateValidator,DateTimeModel,IdentifiactionNumberValidator


# create a tool for availability check the doctor based on date
@tool
def check_doctor_availability(desired_date:DateValidator ,doctor_name:Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe'])->str:
    """Check the availability of doctor on given date
    Args:
        desired_date (DateValidator): date in DD-MM-YYYY format
        doctor_name (Literal): name of the doctor
    Returns:
        str: availability of the doctor slots  on given date
    """
    df=pd.read_csv(r"data\doctor_availability.csv")
    df['date_slot_time'] = df['date_slot'].apply(lambda input: input.split(' ')[-1])
    
    rows = list(df[(df['date_slot'].apply(lambda input: input.split(' ')[0]) == desired_date.date)&(df['doctor_name'] == doctor_name)&(df['is_available'] == True)]['date_slot_time'])

    if len(rows) == 0:
        output = "No availability in the entire day"
    else:
        output = f'This availability for {desired_date.date}\n'
        output += "Available slots: " + ', '.join(rows)

    return output
    
    
@tool
def check_doctor_availability_by_specialization(
        desired_date: DateValidator,
        specialization: Literal[
            'general_dentist', 'cosmetic_dentist', 'prosthodontist',
            'pediatric_dentist', 'emergency_dentist', 'oral_surgeon',
            'orthodontist'
        ]) -> str:
    """Check the availability of doctor on a given date by specialization from the database. if available retuen the avlilable slotes in AM/PM format else return no availability
    
    args:
        desired_date (DateValidator): date in DD-MM-YYYY format
        specialization (Literal): specialization of the doctor
    returns:
        str: availability of the doctors with given specialization on the desired date"""

    df = pd.read_csv(r"data\doctor_availability.csv")

    df['date_slot_time'] = df['date_slot'].apply(lambda x: x.split(' ')[-1])
    df['date_only'] = df['date_slot'].apply(lambda x: x.split(' ')[0])

    mask = (
        (df['date_only'] == desired_date.date) &
        (df['specialization'] == specialization) &
        (df['is_available'] == True)
    )

    filtered = df[mask]

    if filtered.empty:
        return f"No availability in the entire day for {specialization}"

    rows = filtered.groupby(['doctor_name'])['date_slot_time'].apply(list).reset_index()

    def am_to_pm(time_str: str):
        hour, minute = map(int, time_str.split(':'))
        period = "AM"
        if hour >= 12:
            period = "PM"
            if hour > 12:
                hour -= 12
        elif hour == 0:
            hour = 12
        return f"{hour}:{minute:02d} {period}"

    output = f"Availability for {desired_date.date} ({specialization}):\n"

    for _, row in rows.iterrows():
        doctor = row['doctor_name']
        slots = "\n ".join([am_to_pm(t) for t in row['date_slot_time']])
        output += f"- Dr. {doctor}: {slots}\n"

    return output


@tool
def set_appointment(desired_date:DateTimeModel, id_number:IdentifiactionNumberValidator, doctor_name:Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe']):
    """
    
    Check  the available slots. it is available Set appointment slot with the doctor.
    The parameters MUST be mentioned by the user in the query.
    
    args:
        desired_date (DateTimeModel): date and time in DD-MM-YYYY HH:MM format
        id_number (IdentifiactionNumberValidator): identification number of the patient
        doctor_name (Literal): name of the doctor
    returns:
        str: confirmation message of the appointment setting"""
    df = pd.read_csv(r"data\doctor_availability.csv")
   
    from datetime import datetime
    def convert_datetime_format(dt_str):
        dt = datetime.strptime(dt_str, "%d-%m-%Y %H:%M")
        return dt.strftime("%d-%m-%Y %H:%M")  # Also fix the format string here
    
    formatted_datetime = convert_datetime_format(desired_date.date_time)
    
    case = df[(df['date_slot'] == formatted_datetime) & (df['doctor_name'] == doctor_name) & (df['is_available'] == True)]
    
    if len(case) == 0:
        return "No available appointments for that particular case"
    else:
        df.loc[(df['date_slot'] == formatted_datetime) & (df['doctor_name'] == doctor_name) & (df['is_available'] == True), ['is_available','patient_to_attend']] = [False, int(id_number.id)]
        df.to_csv(r"doctor_availability.csv", index=False)
        return "Successfully done"
    

@tool
def cancel_appointment(desired_date:DateTimeModel, id_number:IdentifiactionNumberValidator, doctor_name:Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe']):
    """
    Check the appointement. Cancel appointment slot with the doctor.
    The parameters MUST be mentioned by the user in the query.
    
    args:
        desired_date (DateTimeModel): date and time in DD-MM-YYYY HH:MM format
        id_number (IdentifiactionNumberValidator): identification number of the patient
        doctor_name (Literal): name of the doctor
    returns:
        str: confirmation message of the appointment cancellation
     
    """
    
    df = pd.read_csv(r"data\doctor_availability.csv")
   
    from datetime import datetime
    def convert_datetime_format(dt_str):
        dt = datetime.strptime(dt_str, "%d-%m-%Y %H:%M")
        # Match the exact format in CSV: DD-MM-YYYY HH:MM
        return dt.strftime("%d-%m-%Y %H:%M")
    
    formatted_date = convert_datetime_format(desired_date.date_time)
    
    # Convert id to float to match the CSV data type
    patient_id_float = float(id_number.id)
    
    case = df[
        (df['date_slot'] == formatted_date) & 
        (df['doctor_name'] == doctor_name) & 
        (df['patient_to_attend'] == patient_id_float)
    ]
    
    if len(case) == 0:
        return "No appointment found for that particular case to cancel"
    else:
        df.loc[
            (df['date_slot'] == formatted_date) & 
            (df['doctor_name'] == doctor_name) & 
            (df['patient_to_attend'] == patient_id_float), 
            ['is_available', 'patient_to_attend']
        ] = [True, None]
        
        df.to_csv(r"doctor_availability.csv", index=False)  # Remove the leading space!
        return "Successfully cancelled the appointment"

@tool
def reschedule_appointment(
    desired_date: DateTimeModel, 
    id_number: IdentifiactionNumberValidator, 
    doctor_name: Literal['kevin anderson','robert martinez','susan davis','daniel miller','sarah wilson','michael green','lisa brown','jane smith','emily johnson','john doe'], 
    new_date: DateTimeModel
):
    """
    Reschedule appointment or slot with the doctor.
    The parameters MUST be mentioned by the user in the query.
    Requires: current appointment date/time, patient ID, doctor name, and new desired date/time.
    
    args:
        desired_date (DateTimeModel): current appointment date and time in DD-MM-YYYY HH:MM format
        id_number (IdentifiactionNumberValidator): identification number of the patient
        doctor_name (Literal): name of the doctor
        new_date (DateTimeModel): new desired appointment date and time in DD-MM-YYYY HH:MM format
    returns:
        str: confirmation message of the appointment rescheduling
    """
    
    # First check if new slot is available (before canceling)
    df = pd.read_csv(r"data/doctor_availability.csv")
    from datetime import datetime
    
    def convert_datetime_format(dt_str):
        dt = datetime.strptime(dt_str, "%d-%m-%Y %H:%M")
        return dt.strftime("%d-%m-%Y %H:%M")
    
    new_formatted = convert_datetime_format(new_date.date_time)
    new_slot_check = df[
        (df['date_slot'] == new_formatted) & 
        (df['doctor_name'] == doctor_name) & 
        (df['is_available'] == True)
    ]
    
    if len(new_slot_check) == 0:
        return f"Cannot reschedule: New time slot {new_date.date_time} is not available"
    
    # Now proceed with cancellation and rebooking
    cancel_result = cancel_appointment.invoke({
        "desired_date": desired_date, 
        "id_number": id_number, 
        "doctor_name": doctor_name
    })
    
    if "Successfully cancelled" in cancel_result:
        set_result = set_appointment.invoke({
            "desired_date": new_date, 
            "id_number": id_number, 
            "doctor_name": doctor_name
        })
        
        if "Successfully done" in set_result:
            return f"Successfully rescheduled appointment from {desired_date.date_time} to {new_date.date_time}"
        else:
            # Try to restore the original appointment
            restore = set_appointment.invoke({
                "desired_date": desired_date, 
                "id_number": id_number, 
                "doctor_name": doctor_name
            })
            return f"Failed to book new slot. Original appointment restored: {restore}"
    else:
        return f"Cannot reschedule: {cancel_result}"