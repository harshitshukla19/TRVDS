function submitForm(formId, url) {
    const form = document.getElementById(formId);
    const data = new FormData(form);

    fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': data.get('csrfmiddlewaretoken') },
        body: data
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/user-login.html/user-dashboard.html';
        } else {
            alert(data.error);
        }
    });
}