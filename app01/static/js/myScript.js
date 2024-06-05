$(document).ready(function(){
    $(".read-btn").click(function(){
        var articleId = $(this).data("article-id");
        var fullContentDiv = $("#fullContent" + articleId);

        if (fullContentDiv.is(":visible")) {
            fullContentDiv.slideUp();
        } else {
            $.ajax({
                url: "/article_content/" + articleId + "/",
                method: "GET",
                success: function(data) {
                    if (data.content) {
                        // 使用 HTML 插入内容，以确保换行符替换为 <br> 生效
                        fullContentDiv.html(data.content).slideDown();
                    } else {
                        fullContentDiv.html("<p>Article not found.</p>").slideDown();
                    }
                },
                error: function() {
                    fullContentDiv.html("<p>Error loading article.</p>").slideDown();
                }
            });
        }
    });
});

function confirmDelete() {
    return confirm('Are you sure you want to delete this article?');
}
function confirmUpdate() {
    return confirm('Are you sure you want to Update your information?');
}