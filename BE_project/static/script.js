function scrollToInsights() {
    document.getElementById("insights").scrollIntoView({ behavior: "smooth" });
}

// Display message (Scrapping started)
function displayInitiationMessage() {
    var form = document.querySelector('form');
    var messagePara = document.createElement('p');
    messagePara.id = 'initiationMessage';
    messagePara.textContent = 'Scraping process has begun. Please expect completion within 5 to 6 minutes for retrieval of over 1000 comments.';
    form.parentNode.insertBefore(messagePara, form.nextSibling); //insert msg after form
    document.getElementById('scrappingButton').style.display = 'none'; // hide start scrapping button
    document.getElementById('urlAll').style.display = 'none';  // hide url input
    // document.getElementById('URLLabel').style.display = 'none'; 
}

// function displayLoader() {
//     var loader = document.createElement('div');
//     loader.classList.add('loader');
//     formContainer.appendChild(loader); //insert loader in the form
// }

// Hide message (Scrapping completed )
function hideInitiationMessage() {
    var messagePara = document.getElementById('initiationMessage');
    if (messagePara) {
        messagePara.style.display = 'none';
    }
}

function showAnalysisMessage(){
    var form = document.querySelector('form');
    var anaPara = document.createElement('p');
    anaPara.id = 'analysisMessage';
    anaPara.textContent = 'Preparing Your InsightCo Report!';
    form.parentNode.insertBefore(anaPara, form.nextSibling); //insert msg after form
    document.getElementById('analyzeButton').style.display = 'none'; // hide the analyze sentiment button
}

function hideAnalysisMessage(){
    var anaPara = document.getElementById('analysisMessage');
    if (anaPara) {
        anaPara.style.display = 'none';
    }
}

// function hideLoader() {
//     var loader = document.querySelector('.loader');
//     if (loader) {
//         loader.remove();
//     }
// }

//Scrapping completed
function showNotification() {
    alert('CSV files have been generated!');  //alert when csv files are ready
    // document.getElementById('URLInput').style.display = 'none';  // hide url input
    // document.getElementById('scrappingButton').style.display = 'none'; // hide start scrapping button
    document.getElementById('analyzeButton').style.display = 'inline'; // show sentiment analysis button
}

// Scrapping process
function scrapeAndNotify() {
    var form = document.querySelector('form');
    var videoUrl = form.elements['video_url'].value;  //get url from user

    // display scrapping initiation msg
    displayInitiationMessage();
    // displayLoader();

    // make post request to /scrape endpoint with video url
    fetch('/scrape', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',  //content sent in request body is json type
        },
        body: JSON.stringify({ video_url: videoUrl }),  //convert js obj to json string; videoUrl = variable storing user inputted url
    })
        .then(response => response.json())  //chain a promise (future value that might succeed or fail) to fetch request; json() parse received response as json 
        .then(data => {  //handles parsed json data
            // to indicate scrapping is completed
            // hide scrapping initiation msg
            hideInitiationMessage();
            // hideLoader();
            showNotification();
        })
        .catch(error => {
            console.error('Error:', error);  //to handle errors
        });
    return false; // prevent default form submission
}

// Analyzing process
function analyzeSentiment() {  // make post request to /analyze endpoint with paths to csv files
    // displayLoader();
    showAnalysisMessage();
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            video_details: 'BE_project/csv_files/youtube_video_details.csv',
            comments: 'BE_project/csv_files/youtube_comments.csv',
        }),
    })
        .then(response => response.text()) // chain a promise; extract response as text using text()
        .then(html => { // handler takes resulting text content
            // hideLoader();
            hideAnalysisMessage();
            window.resultHTML = html;  //store html content retrieved into variable
            alert('Sentiment analysis is completed!'); // when analysis completes
            document.getElementById('analyzeButton').style.display = 'none'; // hide the analyze sentiment button
            document.getElementById('openResultButton').style.display = 'inline';  // show the open results button
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function openResult() {
    if (window.resultHTML) {  // is result.html available
        const newWindow = window.open(); // open result.html in new tab
        newWindow.document.write(window.resultHTML);
    } else {
        console.error('No result available');
    }
}