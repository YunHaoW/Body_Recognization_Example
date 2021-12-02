function redirectUrl(clicked_id) {
    window.location.href = 'http://127.0.0.1:3000/comparison/' + clicked_id.toString();
    alert(clicked_id.toString());
}