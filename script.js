document.getElementById('submit-prompt').addEventListener('click', async () => {
    const prompt = document.getElementById('prompt').value;
    const responseOutput = document.getElementById('response-output');

    if (!prompt) {
        responseOutput.innerHTML = '<p>Please enter a prompt.</p>';
        return;
    }

    responseOutput.innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch('/api/gemini', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Set the Content-Type header
            },
            body: JSON.stringify({ prompt: prompt }) // Send the prompt as JSON
        });

        if (!response.ok) {
            // Check content type for error details
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const errorData = await response.json();
                responseOutput.innerHTML = `<p>Error: ${errorData.error}</p>`;
            } else {
                const errorText = await response.text();
                responseOutput.innerHTML = `<p>Error: ${errorText}</p>`;
            }
            return;
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const data = await response.json();
            const markdownText = data.response;
            const html = marked.parse(markdownText);

            responseOutput.innerHTML = html;

            // Tell MathJax to process the new content
            if (window.MathJax) {
                MathJax.typesetPromise([responseOutput])
                    .catch(function (err) {
                        console.log(err.message);
                    });
            } else {
                console.log("MathJax not loaded");
            }
        } else {
            // Handle non-JSON response (e.g., HTML error page)
            const htmlText = await response.text();
            responseOutput.innerHTML = `<p>Unexpected response: ${htmlText}</p>`;
        }

    } catch (error) {
        responseOutput.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});