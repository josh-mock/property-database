import shutil
from flask import Flask, render_template, request, send_file
from datetime import datetime
from functions.download_dataset_helpers import convert_month_to_number, validate_inputs, process_dataset_download, finalize_data_processing, cleanup_temp
from constants import DATASETS_COLUMNS, DATABASE, OUTPUT_FILE_DIRECTORY
from functions.company_search_helpers import get_owner_info, get_titles_for_company, format_titles, format_incorporation_info
from functions.title_search_helpers import get_title_info, format_title_info, get_owners_for_title_number, get_owners_from_raw_owner_info
from functions.export_results_helpers import reset, export_result_as_files, find_file_by_extension, export_title_search_result_as_files


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/download_dataset", methods=["GET", "POST"])
def download_dataset():
    temp_dir = "instance/temp"
    current_year = datetime.now().year
    current_month_start = datetime(
        datetime.now().year, datetime.now().month, 1)

    if request.method == "POST":
        cleanup_temp(temp_dir)
        api_key = request.form.get("api_key")
        download_option = request.form.get("download_option")

        input_month = request.form.get("month")
        input_year = request.form.get("year")
        converted_month = convert_month_to_number(input_month)

        # Validate inputs
        validation_error = validate_inputs(
            api_key, download_option, converted_month, input_year, current_month_start)
        if validation_error:
            return render_template("error.html", message=validation_error, retry_url="download_dataset")

        for dataset in DATASETS_COLUMNS:
            error = process_dataset_download(
                api_key, download_option, dataset, input_year, converted_month)
            if error:
                return render_template("error.html", message=error, retry_url="download_dataset")

        # Finalize data processing
        try:
            finalize_data_processing()
            shutil.rmtree("instance/temp")
            return render_template("download_success.html")
        except Exception as e:
            cleanup_temp(temp_dir)
            return render_template("error.html", message=e, retry_url="download_dataset")

    return render_template("download_dataset.html", current_year=current_year)


@app.route("/company_search", methods=["GET", "POST"])
def company_search():
    if request.method == "POST":
        company = request.form.get("query")

        if not company:
            return render_template("company_search_result.html", owner=company, incorporation_statement=None, titles=None, number_of_properties=None)

        company_details = get_owner_info(DATABASE, company)

        if not company_details:
            return render_template("company_search_result.html", owner=company, incorporation_statement=None, titles=None, number_of_properties=None)

        reset(OUTPUT_FILE_DIRECTORY)

        properties = get_titles_for_company(DATABASE, company)

        incorporation_statement = format_incorporation_info(
            company, company_details)

        titles = format_titles(properties)

        number_of_properties = f"{
            len(titles)} results"

        export_result_as_files(company, incorporation_statement,
                               number_of_properties, titles, OUTPUT_FILE_DIRECTORY)

        return render_template("company_search_result.html", incorporation_statement=incorporation_statement, number_of_properties=number_of_properties, titles=titles)

    return render_template("company_search.html")


@app.route("/title_search", methods=["GET", "POST"])
def title_search():
    if request.method == "POST":
        title_number = request.form.get("query")

        if not title_number:
            return render_template("error.html", message="Missing title number.", retry_url="title_search")

        # Fetch title details
        raw_title_details = get_title_info(DATABASE, title_number)
        formatted_title_details = None
        owners = []

        # Process title details if available
        if raw_title_details:
            formatted_title_details = format_title_info(
                title_number, raw_title_details)
            raw_owner_info = get_owners_for_title_number(
                DATABASE, title_number)
            owners = get_owners_from_raw_owner_info(raw_owner_info)

            # Reset output files and export search results
            reset(OUTPUT_FILE_DIRECTORY)
            export_title_search_result_as_files(
                title_number, formatted_title_details, owners, OUTPUT_FILE_DIRECTORY)

        return render_template(
            "title_search_result.html",
            title_number=title_number,
            address=formatted_title_details["address"] if formatted_title_details else None,
            price=formatted_title_details["price"] if formatted_title_details else None,
            owners=owners
        )

    return render_template("title_search.html")


@app.route("/download_pdf")
def download_pdf():
    pdf_file_path = find_file_by_extension(OUTPUT_FILE_DIRECTORY, ".pdf")
    return send_file(pdf_file_path, as_attachment=True)


@app.route("/download_csv")
def download_csv():
    csv_file_path = find_file_by_extension(OUTPUT_FILE_DIRECTORY, ".csv")
    return send_file(csv_file_path, as_attachment=True)


if __name__ == "__main__":
    app.run()
