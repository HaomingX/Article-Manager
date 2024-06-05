$(document).ready(function(){
    $(".read-btn").click(function(){
        console.log("read-btn clicked")
        var articleId = $(this).data("article-id");
        var fullContentDiv = $("#fullContent" + articleId);
        var llmSummaryDiv = $('#llm-summary-' + articleId);

        // Hide all other full content and summaries
        $('.full-content').not(fullContentDiv).hide();

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

        llmSummaryDiv.hide();
    });

    $('.llm-explain-btn').click(function(){
        var articleId = $(this).data('article-id');
        var summaryDiv = $('#llm-summary-' + articleId);
        var fullContentDiv = $('#fullContent' + articleId);

        // Hide all other summaries and full content
        $('.full-content').not(summaryDiv).hide();

        // Check if the summary is already cached
        if (summaryDiv.data('cached')) {
            summaryDiv.toggle();
            return;
        }

        $.ajax({
            url: '/llm_explain/',
            method: 'POST',
            data: {
                'article_id': articleId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                summaryDiv.html(response.summary);
                summaryDiv.data('cached', true); // Mark as cached
                summaryDiv.show();
            },
            error: function(response) {
                alert('Error occurred while processing LLM explain.');
            }
        });
        fullContentDiv.hide();
    });
});

function confirmDelete() {
    return confirm('Are you sure you want to delete this article?');
}


