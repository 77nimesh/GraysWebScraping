# Grays Scraping Using Async

This project scrapes auctioned and sold car details and prices from Grays, saving the data into a database. This allows for easy car valuation in the market.

## Usage

1. Clone the Git repository:

    ```bash
    git clone <repository_url>
    ```

2. Navigate to the project directory:

    ```bash
    cd GraysScrapingUsingAsync
    ```

3. Rebuild the Docker image:

    ```bash
    docker build -t grays_scraper .
    ```

4. Run the container with volume mounting:

    ```bash
    docker run --rm -v "$(pwd):/app" grays_scraper
    ```

## Features

- 🚀 **Asynchronous Web Scraping**: Efficiently scrape data using async operations.
- 💾 **Database Storage**: Save auctioned and sold car details into a database.
- 📊 **CSV Export**: Generate CSV files for further analysis and car valuation.

## Usage Guidelines

- Ensure Docker is installed on your system.
- Update `car_links_to_scrape.csv` with the latest auction links.
- Run the Docker container to start scraping.
- Check the generated CSV files for the scraped data.

## Troubleshooting

- 🛠️ **Docker Build Issues**: Ensure you have the correct Dockerfile and dependencies.
- 📂 **CSV File Format**: Verify the CSV files are in the correct format and accessible.
- 🐛 **Runtime Errors**: Check Docker logs for any runtime errors.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- 🙏 Thanks to the contributors and the open-source community.
- 📈 Special thanks to Grays for providing the data source.

