 var csrftoken = '{{ csrf_token }}';

    function csrfSafeMethod(method) {
        // 这些HTTP方法不要求CSRF保护
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    // Setup Ajax for CSRF Token
    function setupAjax() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
function updateCategory2() {
            var category1Id = document.getElementById('id_category1').value;
            // 发送AJAX请求获取子类别数据
            fetch(`/publish?parentId=${category1Id}`)
                .then(response => response.json())
                .then(data => {
                    var category2Select = document.getElementById('id_category2');
                    // 清除现有的选项
                    category2Select.innerHTML = '';
                    // 添加新的选项
                    data.forEach(function(subcategory) {
                        var option = new Option(subcategory.name, subcategory.id);
                        category2Select.add(option);
                    });
                     // 更新Category3的选项
                    updateCategory3(); // 假设Category3的更新依赖于Category2的选中值
                })
                .catch(error => console.error('Error:', error));
        }

function updateCategory3() {
            var category2Id = document.getElementById('id_category2').value;
            // print(category2Id);
            // 发送AJAX请求获取子类别数据
            fetch(`/publish?parentId=${category2Id}`)
                .then(response => response.json())
                .then(data => {
                    var category2Select = document.getElementById('id_category3');
                    // 清除现有的选项
                    category2Select.innerHTML = '';
                    // 添加新的选项
                    data.forEach(function(subcategory) {
                        var option = new Option(subcategory.name, subcategory.id);
                        category2Select.add(option);
                    });
                })
                .catch(error => console.error('Error:', error));
        }
        function addCategory(level) {
            var name = prompt("Enter new category name:");
            if (name) {
                var parent_id = null;
                if (level == 1) {
                    parent_id = null;
                }
                if (level == 2) {
                    parent_id = document.getElementById('id_category1').value;
                    if (!parent_id) {
                        alert("Please select a Category1 first.");
                        return;
                    }
                }
                if (level == 3) {
                    parent_id = document.getElementById('id_category2').value;
                    if (!parent_id) {
                        alert("Please select a Category2 first.");
                        return;
                    }
                }

                fetch('/publish/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: new URLSearchParams({
                        'name': name,
                        'level': level,
                        'parent': parent_id
                    })
                })
                .then(response => response.json())
                .then(data => {
                    var option = new Option(data.name, data.id);
                    if (level == 1) {
                        document.getElementById('id_category1').add(option);
                    } else if (level == 2) {
                        document.getElementById('id_category2').add(option);
                    }
                    else if (level == 3) {
                        document.getElementById('id_category3').add(option);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        }
