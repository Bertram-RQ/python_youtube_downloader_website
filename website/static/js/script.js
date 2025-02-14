document.getElementById("form").addEventListener("submit", async function (event) {
    /* by bertramrq: https://www.youtube.com/@BertramRQ */
    event.preventDefault();

    // get type (video/audio)
    const selectedType = document.getElementById("input-menu-type").value;
    console.log(selectedType)

    let selectedFormat

    if (selectedType === "audio") {
        selectedFormat = document.getElementById("input-menu-format-audio").value;
        console.log(selectedFormat);
    } else {
        selectedFormat = document.getElementById("input-menu-format-video").value;
        console.log(selectedFormat);
    }


    // Get the values from the input bar and input menu
    const inputValue = document.getElementById("input-bar").value;
    const selectedOption = document.getElementById("input-menu-resolution").value;
    console.log(selectedOption)

    // Check if the input value starts with one of the allowed prefixes
    const real_youtube_links = ["https://www.youtube.com", "https://youtube.com", "https://youtu.be"]
    const real_Tiktok_links = ["https://www.tiktok.com", "https://m.tiktok.com"]

    // Check if the string starts with any of the prefixes in the list
    let startsWithPrefix = false;
    let isYoutubeVideo = false;
    let isTiktokVideo = false;
    for (let i = 0; i < real_youtube_links.length; i++) {
        if (inputValue.startsWith(real_youtube_links[i])) {
            startsWithPrefix = true;
            isYoutubeVideo = true;
            break;  // Exit loop as soon as we find a match
        }
    }
    for (let i = 0; i < real_Tiktok_links.length; i++) {
        if (inputValue.startsWith(real_Tiktok_links[i])) {
            startsWithPrefix = true;
            isTiktokVideo = true;
        }
    }

    // if (selectedType === "audio" && isTiktokVideo) {
    //     alert("unable to download tiktok videos as audio only sorry");
    //     return;
    // }

    console.log(startsWithPrefix)
    console.log(isYoutubeVideo)
    console.log(isTiktokVideo)

    if (!startsWithPrefix) {
        alert(`Input URL must start with a valid prefix (${real_youtube_links[0]}, ${real_youtube_links[1]}, ${real_youtube_links[2]}).`);
        return;
    }

    // Generate a unique ID for the card (using current timestamp)
    const cardId = Date.now();

    // Create a new card with the unique ID
    const card = document.createElement("div");
    card.classList.add("card");
    card.id = `card-${cardId}`;  // Set the unique ID as the card's ID

    // Add the input bar and input menu values to the card
    if (selectedType === "audio") {
        card.innerHTML = `
        <div class="thumbnail-div"></div>
        <h3 class="card-download-info">Downloading:<a class="card-download-info-a"> ${inputValue}</a></h3>
        <p class="card-info time-taken">Took: ...</p>
        <p class="card-info card-type">Type: ${selectedType}</p>
        <p class="card-info">Format: ${selectedFormat}</p>
        <button class="download-button button--loading" disabled><span class="button-text button__text">Wait...</span></button>
    `;
    } else {
        card.innerHTML = `
        <div class="thumbnail-div"></div>
        <h3 class="card-download-info">Downloading:<a class="card-download-info-a"> ${inputValue}</a></h3>
        <p class="card-info time-taken">Took: ...</p>
        <p class="card-info card-type">Type: ${selectedType}</p>
        <p class="card-info">Format: ${selectedFormat}</p>
        <p class="card-info card-resolution-info">Selected Resolution: ${selectedOption}</p>
        <button class="download-button button--loading" disabled><span class="button-text button__text">Wait...</span></button>
    `;
    }

    let platform

    if (isTiktokVideo) {
        platform = "tiktok";
    } else {
        platform = "youtube";
    }

    let server_ip = await getServerIP();

    console.log(server_ip)




    const downloads_label = document.getElementById("downloads");
    downloads_label.style.display = "unset"
    downloads_label.style.marginTop = "20px"

    // Add the card to the cards container
    document.getElementById("cards-container").prepend(card);

    // Send the form data and unique card ID to the server via a POST request
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'input-menu-type': selectedType,
            'format': selectedFormat,
            'input-bar': inputValue,
            'input-menu-resolution': selectedOption,
            'card-id': cardId,  // Send the card's unique ID
            'platform': platform,
            'server-ip': server_ip,
        })
    })
        .then(response => response.json())
        .then(data => {
            const downloadButton = card.querySelector(".download-button");
            const downloadButtonText = card.querySelector(".button-text");


            if (data.should_keep === false) {
                card.remove()
                const downloadsH2 = document.getElementById("downloads")
                downloadsH2.style.display = "none"
                console.log(`told to not keep: ${data.card_id}`)
                return
            }

            console.log(data.video_platform)


            if (data.selected_type === "video") {
                const cardResolutionInfo = card.querySelector(".card-resolution-info");
                console.log(cardResolutionInfo)
                if (data.video_platform === "tiktok") {
                    cardResolutionInfo.textContent = `Resolution: ???`;
                } else {
                    cardResolutionInfo.textContent = `Resolution: ${data.best_available_resolution}`
                }
            };

            // `Downloaded: ${data.video_title}`

            // `Downloaded: <a href="${data.video_url}">wdoijwaoijd</a>`

            const thumbnailDiv = card.querySelector(".thumbnail-div");
            console.log(thumbnailDiv)
            thumbnailDiv.style = "max-width: 50%; max-height: 80%"

            const thumbnailImage = document.createElement("img");
            thumbnailImage.src = data.video_thumbnail_link;
            // thumbnailImage.style = "max-width: 50%; max-height: 80%"
            thumbnailImage.classList.add("thumbnail-image");

            thumbnailDiv.appendChild(thumbnailImage);

            const downloadInfo_a = card.querySelector(".card-download-info-a");
            const downloadInfo = card.querySelector(".card-download-info");

            console.log(downloadInfo_a)
            console.log(downloadInfo)

            downloadInfo_a.textContent = `${data.video_title}`
            downloadInfo_a.href = `${data.video_url}`

            downloadInfo.textContent = `Downloaded: `

            //  downloadInfoLink.innerHTML = `
            //      <a href="${data.video_url}">${data.video_title}</a>
            //  `

            const downloadInfoLink = document.createElement("a");
            downloadInfoLink.classList.add("download-info-link");
            downloadInfoLink.textContent = `${data.video_title}`;
            downloadInfoLink.href = `${data.video_url}`;
            downloadInfoLink.target = `_blank`

            const downloadInfoH3Num1 = document.createElement("h3");
            downloadInfoH3Num1.textContent = `By: `
            downloadInfoH3Num1.style.fontSize = "15px"

            const downloadInfoChannelLink = document.createElement("a");
            downloadInfoChannelLink.classList.add("download-info-link");
            downloadInfoChannelLink.classList.add("download-info-channel-link")
            downloadInfoChannelLink.textContent = `${data.video_channel_name}`;
            downloadInfoChannelLink.href = `${data.video_channel_link}`;
            downloadInfoChannelLink.target = `_blank`


            downloadInfo.appendChild(downloadInfoLink)
            downloadInfoH3Num1.appendChild(downloadInfoChannelLink)
            downloadInfo.appendChild(downloadInfoH3Num1)

            card.classList.add("card-downloaded");




            console.log(`${data.video_url}`)
            console.log(`${data.video_title}`)

            // downloadInfo_a.textContent = `${data.video_title}`;
            // downloadInfo_a.href = data.video_url


            const timeTaken = card.querySelector(".time-taken");
            timeTaken.textContent = `Took: ${data.time_taken}s`


            downloadButtonText.classList.remove("button__text");


            // Enable the download button and update the link after receiving the download link from the server
            downloadButton.disabled = false;
            downloadButton.classList.remove("button--loading");
            downloadButton.classList.add("enabled");
            // downloadButton.textContent = "Download"
            downloadButtonText.textContent = "Download"
            downloadButton.onclick = function () {
                window.location.href = data.download_link;  // Use the link received from the server
            };
        })
        .catch(error => {
            console.error("Error:", error);
        });

});

// function toggleMenu() {
//     const menu = document.getElementById("mobileMenu");
//     if (menu.style.display === "flex") {
//         menu.style.display = "none";
//     } else {
//         menu.style.display = "flex";
//     }
// }

/* by bertramrq: https://www.youtube.com/@BertramRQ */
function toggleType() {
    let selectedType = document.getElementById("input-menu-type").value;
    //  let videoContent = [document.getElementById("input-menu-format-video"), document.getElementById("input-menu-resolution")]
    //  let audioContent = [document.getElementById("input-menu-format-audio")]

    let videoContent = document.getElementsByClassName("video-element");
    let audioContent = document.getElementsByClassName("audio-element");

    console.log(selectedType)

    if (selectedType === "video") {
        for (let i = 0; i < videoContent.length; i++) {
            videoContent[i].style.display = "block"
        }
        for (let i = 0; i < audioContent.length; i++) {
            audioContent[i].style.display = "none"
        }
    } else {
        for (let i = 0; i < videoContent.length; i++) {
            videoContent[i].style.display = "none"
        }
        for (let i = 0; i < audioContent.length; i++) {
            audioContent[i].style.display = "block"
        }
    }


}
/* by bertramrq: https://www.youtube.com/@BertramRQ */
document.getElementById("remove-files").addEventListener("click", function (event) {
    console.log(`pressed: ${event}`)

    const downloadsH2 = document.getElementById("downloads")
    downloadsH2.style.display = "none"

    let cards = Array.from(document.getElementById("cards-container").children);
    cards.forEach(card => card.remove());


    // Send the form data and unique card ID to the server via a POST request
    fetch('/files', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
})


async function getServerIP() {
    try {
        let response = await fetch('/server-ip');  // Wait for response
        let data = await response.json();         // Wait for JSON parsing
        console.log('Connected to Server IP:', data.server_ip);
        return data.server_ip;                    // Return the IP if needed
    } catch (error) {
        console.error('Error fetching server IP:', error);
    }
}