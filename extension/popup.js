let scrapePosts = document.getElementById("scrapePosts");
// fallback to 5

scrapePosts.addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const postCountInput = document.getElementById("postCount");
    const targetScrapes = parseInt(postCountInput.value, 10) || 0; 
    // Then run your scraping logic
    await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: scrapePostsFromPage,
        args: [targetScrapes]
    });
});


function scrapePostsFromPage(targetScrapes = 0) {
    const closePostXPath = "//*[starts-with(@id, 'mount_0_0')]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[3]/div | //*[starts-with(@id, 'mount_0_0')]/div/div[1]/div/div[4]/div/div[not(@hidden)]/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[3]/div";
    const scrapePostXPath = "//*[starts-with(@id, 'mount_0_0')]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div";
    const scrapeGroupNameXPath = "//*[starts-with(@id, 'mount_0_0')]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div[1]/div/div[1]/h1/span/a"
    const allCommentSpanXPath = "//span[contains(text(), 'Comment')]";//"//span[text() = 'm']";//
    const allCopySpanXPath = "//span[contains(text(), 'Copy')]";

    function getElementsByXpath(xpath) {
        const results = [];
        const snapshot = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < snapshot.snapshotLength; i++) {
            results.push(snapshot.snapshotItem(i));
        }
        return results;
    }

    function getElementByXpath(xpath) {
        const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
        return result.singleNodeValue;
    }

    function waitForXPath(xpath, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const intervalTime = 100;
            let timeElapsed = 0;

            const interval = setInterval(() => {
                const element = getElementByXpath(xpath);
                if (element) {
                    clearInterval(interval);
                    resolve(element);
                } else {
                    timeElapsed += intervalTime;
                    if (timeElapsed >= timeout) {
                        clearInterval(interval);
                        reject(new Error("Element not found: " + xpath));
                    }
                }
            }, intervalTime);
        });
    }

    function extractTextWithSpaces(node) {
        let text = '';
        node.childNodes.forEach(child => {
          if (child.nodeType === Node.TEXT_NODE) {
            text += child.textContent + ' ';
          } else if (child.nodeType === Node.ELEMENT_NODE) {
            text += extractTextWithSpaces(child) + ' ';
          }
        });
        return text.trim();
      }

    function getFormattedDateTime() {
        const now = new Date();
    
        const pad = n => n.toString().padStart(2, '0');
    
        const day = pad(now.getDate());
        const month = pad(now.getMonth() + 1); // Months are 0-based
        const year = now.getFullYear();
        const hours = pad(now.getHours());
        const minutes = pad(now.getMinutes());
        const seconds = pad(now.getSeconds());
    
        return `${day}${month}${year}${hours}${minutes}${seconds}`;
    }

    const scrapedPosts = [];
    // MAIN FUNCTION: using async IIFE to handle await in loop
    (async () => {
        const processedComments = new Set();
        const copiedLinks = new Set();
        // const targetScrapes = 5;
        let totalScraped = 0;

        let groupName = "houses";
        let groupLink = "houses";
        
        const scrapeGroupNameElement = getElementByXpath(scrapeGroupNameXPath);
        if (scrapeGroupNameElement) {
          try {
            groupName = scrapeGroupNameElement.innerText.trim() || "houses";
            groupLink = scrapeGroupNameElement.href || "houses";
            console.log(`Scraping Group Name: ${groupName}`);
            console.log(`Scraping Group Link: ${groupLink}`);
          } catch (err) {
            console.warn("Failed to extract group name or link, using fallback.");
          }
        } else {
          console.warn("Group name element not found, using fallback.");
        }

        scrapedPosts.push(groupLink);

        while (totalScraped < targetScrapes) {
            const currentLinksElements = getElementsByXpath(allCopySpanXPath);
            const currentCommentSpans = getElementsByXpath(allCommentSpanXPath);
            const newCommentSpans = currentCommentSpans.filter(item => !processedComments.has(item));
            const newLinks = currentLinksElements.filter(item => !copiedLinks.has(item));
            if (newCommentSpans.length === 0) {
                console.log("No new comments found. Scrolling down...");
                window.scrollBy(0, 1000);
                await new Promise(resolve => setTimeout(resolve, 1000));
                continue;
            }

            if (newCommentSpans.length === 0) {
                console.log("No new links found. Scrolling down...");
                window.scrollBy(0, 1000);
                await new Promise(resolve => setTimeout(resolve, 1000));
                continue;
            }
    
            for (let i = 0; i < newCommentSpans.length && totalScraped < targetScrapes; i++) {
                const commentElement = newCommentSpans[i];
                const copyLinkElement = newLinks[i];

                processedComments.add(commentElement); // Mark as processed

                // console.log(`Clicking copy link ${totalScraped + 1} of ${targetScrapes}`);
                // copyLinkElement.click();
                // copiedLinks.add(copyLinkElement);

                console.log(`Clicking comment ${totalScraped + 1} of ${targetScrapes}`);
                const event = new MouseEvent("click", {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                commentElement.dispatchEvent(event);
                // commentElement.click();
    
                try {
                    const scrapePostElement = await waitForXPath(scrapePostXPath, 5000);
                    const html  = extractTextWithSpaces(scrapePostElement).replace(/^[\s\S]*?Shared with Public group/, '').replace(/\b(?:[\da-zA-Z]\s+){9,}[\da-zA-Z]\b/g, '');
                    scrapedPosts.push(html);
                    console.log(`Scraped post ${totalScraped + 1}: ${html}`);

                } catch (err) {
                    console.log(`Failed to scrape post ${totalScraped + 1}: ${err.message}`);
                }
    
                try {
                    const closePostElement = await waitForXPath(closePostXPath, 5000);
                    closePostElement.click();
                    console.log(`Closed post ${totalScraped + 1}`);
                } catch (err) {
                    console.log(`Error closing post ${totalScraped + 1}: ${err.message}`);
                }
    
                totalScraped++;

                await new Promise(resolve => setTimeout(resolve, 1000));
            }
    
            window.scrollBy(0, 1000);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        console.log(`Done scraping ${totalScraped} posts.`);
        const csvContent = "data:text/csv;charset=utf-8," +
  scrapedPosts.map(row => {
    const cleanedRow = row
      .replace(/[!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/g, '') // Remove punctuation
      .replace(/"/g, '""') // Escape quotes for CSV
      .replace(/\r?\n|\r/g, ' '); // Remove line breaks

    return `"${cleanedRow}"`;
  }).join("\n");
 // Replace line breaks with spaces
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        const date = getFormattedDateTime();
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `${groupName}_${date}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log("Final scrapedPosts length:", scrapedPosts.length);
console.log("Sample post:", scrapedPosts[1]);


        console.log(`Downloaded ${scrapedPosts.length} posts to CSV`);
    })();
}
