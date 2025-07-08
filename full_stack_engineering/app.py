import gradio as gr
from donor_eligibility import DonorEvaluator

def evaluate_donor_eligibility(
    donor_name,
    age,
    gender,
    weight,
    weight_unit,
    height,
    height_unit,
    hemoglobin,
    last_donation_date
):
    try:
        kwargs = dict(
            donor_name_or_id=donor_name.strip() if donor_name else None,
            age=int(age),
            gender=gender,
            weight=float(weight),
            weight_unit=weight_unit,
            height=float(height),
            height_unit=height_unit,
            hemoglobin=float(hemoglobin)
        )
        if last_donation_date and last_donation_date.strip():
            kwargs["last_donation_date"] = last_donation_date.strip()
        evaluator = DonorEvaluator(**kwargs)
        result = evaluator.evaluate()
        eligibility_status = result.get("eligibility_status", "")
        tbv = f"{result.get('total_blood_volume_l','')} L"
        max_draw = f"{result.get('max_draw_volume_ml','')} mL"
        reason = ", ".join(result["reasons"]) if result.get("reasons") else "None"
        days = result.get("days_since_last_donation")
        days_str = f"{days} days" if days is not None else "N/A"
    except Exception as e:
        eligibility_status = "❌ Error"
        tbv = ""
        max_draw = ""
        reason = str(e)
        days_str = ""
    return eligibility_status, tbv, max_draw, reason, days_str

with gr.Blocks(title="Blood Donor Eligibility Screening") as app:
    gr.Markdown(
        "<h2>Blood Donor Eligibility Screening</h2>"
        "<p>Fill in donor information to assess blood donation eligibility.</p>"
    )
    with gr.Row():
        with gr.Column():
            donor_name = gr.Textbox(label="Donor Name or ID (optional)")
            age = gr.Number(label="Age", minimum=0, step=1, value=18)
            gender = gr.Radio(label="Gender", choices=["Male", "Female", "Other"], value="Male")
            weight = gr.Number(label="Weight", minimum=0, value=70)
            weight_unit = gr.Dropdown(label="Weight Unit", choices=["kg", "lbs"], value="kg")
            height = gr.Number(label="Height", minimum=0, value=170)
            height_unit = gr.Dropdown(label="Height Unit", choices=["cm", "inches"], value="cm")
            hemoglobin = gr.Number(label="Hemoglobin (g/dL)", minimum=0, value=13.5)
            last_donation_date = gr.Textbox(label="Last Donation Date (YYYY-MM-DD, optional)", placeholder="YYYY-MM-DD")
            btn = gr.Button("Evaluate Eligibility")
        with gr.Column():
            output_status = gr.Textbox(label="Eligibility Status", interactive=False)
            output_tbv = gr.Textbox(label="Estimated TBV (L)", interactive=False)
            output_max_draw = gr.Textbox(label="Max Draw Volume (mL)", interactive=False)
            output_reason = gr.Textbox(label="Reason for Ineligibility", interactive=False)
            output_days = gr.Textbox(label="Days Since Last Donation", interactive=False)
    btn.click(
        evaluate_donor_eligibility,
        [
            donor_name,
            age,
            gender,
            weight,
            weight_unit,
            height,
            height_unit,
            hemoglobin,
            last_donation_date
        ],
        [
            output_status,
            output_tbv,
            output_max_draw,
            output_reason,
            output_days
        ]
    )

app.launch(share=True)