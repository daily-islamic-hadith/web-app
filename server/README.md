# Daily Islamic Hadith Web Service

Welcome to the **Daily Islamic Hadith Web Service** repository! This project is a Flask-based web application designed
to provide a
daily Hadith from the vast collections of Islamic traditions.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Contributing](#contributing)
- [License](#license)

## Features

- **RESTful Web Service**: A backend service that provides the daily Hadith data, accessible via API.
- **Lightweight**: Minimal dependencies and lightweight code for efficient performance.
- **Open Source**: Free to use, modify, and distribute.

## Installation

### Prerequisites

Ensure you have Python >= 3.10 installed on your system. You can check your Python version with:

```bash
python3 --version
```

You should also have `pip` (Python package installer) available.

### Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/osama1225/daily-islamic-hadith.git
cd daily-islamic-hadith/server
```

### Set Up a Virtual Environment (Optional but Recommended)

Create and activate a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies

Install the necessary Python packages using `pip`:

```bash
pip install --upgrade pip       # upgrade it first
pip install -r requirements.txt # install dependencies
```

## Usage

### Running the Flask Application

After installing the dependencies, start the Flask application:

```bash
flask --app server/hadith_app run
```

The app should now be running on `http://127.0.0.1:5000/`. You can visit this URL in your web browser to view the daily
Hadith.

## Data Sources

This project utilizes Hadith collections from reliable and authentic sources, including:

- Sahih Bukhari
- Sahih Muslim
- Sunan Abu Dawood
- And other major Hadith collections

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a new Pull Request.

Please ensure your code follows the project's coding standards and includes tests for any new functionality.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
