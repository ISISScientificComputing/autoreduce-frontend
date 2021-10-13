function update_page(item) {
    let per_page = document.getElementById("select_per_page").value;
    document.location.href = document.location.href + "&per_page=" + per_page;
}