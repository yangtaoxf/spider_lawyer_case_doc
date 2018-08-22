(function ($, window, document, undefined) {
    var Params = function (element, options) {
        this.$element = $(element);
        this.defaults = {
            data: {
                Elements: [],
                RelateInfo: [],
                LegalBase: []
            }
        };
        this.settings = $.extend({}, this.defaults, options);
    };
    Params.prototype = {
        Init: function () {
            this.BindData();
            $(".div_container").append(this.BuildItemsData());
            this.BindEvent();

        },
        BindData: function () {
            var htmlObj = this.BuildHtmlContainer();
            this.$element.append(htmlObj);
            return this.$element;
        },
        //创建控件父容器
        BuildHtmlContainer: function () {
            var $ul = $("<ul></ul>");
            var $li = $("<li class=\"attribute\"></li>");
            var $a = $(" <a href=\"#\" class=\"outline tool_dir_common\">概要</a> ");
            var $divInfo = $("<div class=\"info\"></div>");
            var $divIconBottom = $("<div class=\"icon\"><img src=\"http://wenshu.court.gov.cn/Assets/img/content/content_directory_spot2.png\" /></div>");
            $divInfo = $divInfo.append(this.BuildHtmlContent().append($divIconBottom));
            $li = $li.append($a).append($divInfo);
            $ul = $ul.append($li);
            return $ul;
        },
        BuildHtmlContent: function () {
            var jsonData = this.settings.data;
            var $container = $("<div class=\"con\"></div>");
            var $divIconTop = $("<div class=\"icon\"><img src=\"http://wenshu.court.gov.cn/Assets/img/content/content_directory_spot2.png\" /></div>");
            $container.append($divIconTop);
            var eles = jsonData.Elements;
            if (eles.length == 0) {
                $("#divTool_Summary").hide();
            }
            if ($.isArray(eles) && eles.length > 0) {
                //中国裁判文书网和大数据系统共用，依次作为区分
                var pageType = $("#hidPageType").val();
                var page = "ListBigData";
                if (pageType != "BIGDATA") { page = "List"; }
                for (var j = 0; j < eles.length; j++) {
                    switch (eles[j]) {
                        case "RelateInfo":
                            //创建文书关联信息
                            var relateInfo = jsonData.RelateInfo;
                            var $promptHtml = this.BuildPromptHtml("基本信息");
                            var html = "<div class='relateinfo'>";
                            if ($.isArray(relateInfo)) {
                                if (relateInfo.length > 0) {
                                    html += "<table class='table_info'>"
                                    for (var i = 0; i < relateInfo.length; i++) {
                                        var noLink = "案号|审理程序|裁判日期|审判人员|公诉机关|书记员|上诉人|当事人";
                                        if (relateInfo[i] != undefined && relateInfo[i].value != "") {
                                            var name = relateInfo[i].name;
                                            var val = relateInfo[i].value;
                                            if (relateInfo[i].name != "案件类型" && relateInfo[i].name != "案由") {
                                                if (noLink.indexOf(name) >= 0 && val != "" && val != "无") {
                                                    html += "<tr><th>&nbsp;&nbsp;" + name + "：</th><td>" + val + "</td></tr>";
                                                } else {
                                                    if (relateInfo[i].value != "" && val != "" && val != "无") {
                                                        var searchName = name;
                                                        if (name == "审理法院") { searchName = "法院名称"; }
                                                        html += "<tr><th>&nbsp;&nbsp;" + name + "：</th><td><a target='_blank' href=\"/List/" + page + "?sorttype=1&conditions=searchWord++" + searchName + "+" + val + "+" + searchName + ":" + val + "\">" + val + "</a></td></tr>"
                                                    }
                                                }
                                            } else {
                                                html += "<tr><th>&nbsp;&nbsp;" + name + "：</th><td><a target='_blank' href=\"/List/" + page + "?sorttype=1&conditions=searchWord++" + name + "+" + val + "+" + name + ":" + val + "\">" + val + "</a></td></tr>"
                                            }
                                        }
                                    }
                                    html += "</table>"
                                } else {
                                    html = html + " <div class='basic_no_info'>&nbsp;&nbsp;此项无内容！</div>";
                                }
                            }
                            html = html + "</div>";
                            var $conHtml = $(html);
                            $container.append($promptHtml).append($conHtml);
                            break;
                        case "LegalBase":
                            //创建法律依据
                            var legalBase = jsonData.LegalBase;
                            if ($.isArray(legalBase) && legalBase.length > 0) {
                                var $promptHtml = this.BuildPromptHtml("法律依据");
                                var htmlDiv = " <div class='relateinfo'>";
                                var html = "   <table>";
                                var actCount = 0;
                                for (var i = 0; i < legalBase.length; i++) {
                                    var items = legalBase[i].Items;
                                    var itemCount = 0;
                                    if (items != undefined) {
                                        var itemNames = "";
                                        var htmlItem = "";
                                        for (var j = 0; j < items.length; j++) {
                                            var itemName = items[j].法条名称;
                                            itemName = itemName.substr(0, itemName.indexOf('条') + 1);
                                            if (itemNames.indexOf(itemName) < 0) {
                                                if (items[j].法条内容.indexOf("系统尚未收录或引用有误") < 0) {
                                                    itemCount = 1;
                                                    htmlItem = htmlItem + " <tr>";
                                                    htmlItem = htmlItem + "        <td clss='relate_doc_td2'>&nbsp;&nbsp;&nbsp;&nbsp;<a name='actItem' href=\"javascript:void(0);\">" + itemName + "</a></td>";
                                                    htmlItem = htmlItem + " </tr>";
                                                }
                                                itemNames = itemNames + itemName + ",";
                                            }
                                        }
                                    }

                                    if (itemCount > 0 && legalBase[i].法规名称 != "") {
                                        actCount = 1;
                                        html = html + " <tr>";
                                        html = html + "        <td clss='relate_doc_td2'>&nbsp;&nbsp;" + legalBase[i].法规名称 + "</td>";
                                        html = html + " </tr>";
                                        html = html + htmlItem;
                                    }
                                }
                                html = html + "  </table>";
                                if (actCount > 0) { htmlDiv = htmlDiv + html + "</div>"; } else { htmlDiv = ""; }
                                var $conHtml = $(htmlDiv);
                                if ($conHtml != undefined && $conHtml.length > 0) {
                                    $container.append($promptHtml).append($conHtml);
                                }
                            }
                            break;
                        default:
                            break;
                    }
                }
            } else {
                var $container = $("<div style=\"color:#B91516;\">无此文书的概要信息！</div>");
            }
            return $container;
        },
        //创建提示语容器
        BuildPromptHtml: function (prompt) {
            var html = " <div class=\"content_tool_common\">";
            html = html + " <div class=\"content_info_common\" >" + prompt + "</div>";
            html = html + " </div>";
            return $(html);
        },
        //创建法条关联信息
        BuildItemsData: function () {
            //2015年11月23日 wangzhange divLawItems 弹出框的宽度自适应和高度固定 content_lawitems_body固定高度数据过多时出现滚动条
            var $container = $("<div id=\"divLawItems\" class=\"divcontent_comment display_none\" style=\"width:auto;height:480px;position: absolute;top:261px;\">"); //2015年11月23日
            $container = $container.append("<div class=\"content_comment_head\"><table><tr><td class=\"info\">法律依据</td><td class=\"close\"><img style=\"cursor: pointer;\" alt=\"点击关闭\" src=\"http://wenshu.court.gov.cn/Assets/img/content/content_comment_close.png\"onclick=\"$('#divLawItems').hide();\" /></td></tr></table></div>");
            var $lawItemsBody = $("<div class=\"content_lawitems_body\" style='height:456px;overflow-y:auto;'></div>");
            var $lawItemsTbl = $("<table id=\"comment_item_table\"></table>");
            var jsonData = this.settings.data;
            var legalBase = jsonData.LegalBase;
            if ($.isArray(legalBase) && legalBase.length > 0) {
                for (var i = 0; i < legalBase.length; i++) {
                    var itemHtml = "<tr class=\"comment_font\">";
                    itemHtml += "       <td>";
                    itemHtml += "          " + legalBase[i].法规名称 + "";
                    itemHtml += "       </td>";
                    itemHtml += "</tr>";

                    var items = legalBase[i].Items;
                    for (var j = 0; j < items.length; j++) {
                        if (items[j].法条内容.indexOf("系统尚未收录或引用有误") < 0) {
                            itemHtml += "<tr class=\"comment_font\">";
                            itemHtml += "<td>";
                            itemHtml += items[j].法条内容.replace(/\[ly\]/g, "</br>").replace(/&amp;#xA;/g, "</br>") + "";
                            itemHtml += "</td>";
                            itemHtml += "</tr>";
                        }
                    }
                    $lawItemsTbl = $lawItemsTbl.append($(itemHtml));
                }
            } else {
                var itemHtml = "<tr class=\"comment_font\">";
                itemHtml += "       <td style=\"color:#B91516;\">";
                itemHtml += "&nbsp;&nbsp;无法律依据数据！";
                itemHtml += "</td>";
                itemHtml += "</tr>";
                $lawItemsTbl.append($(itemHtml));
            }
            $lawItemsTbl.append("<tr class=\"comment_font\"><td><div class=\"lawitems_statement\"><div class=\"statement_head\">免责声明</div><div class=\"statement_body\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;法律依据仅供参考，如有需要，请您在核实裁判文书与相应法律、法规版本后慎重使用，并自行承担法律后果。</div></div></td></tr>");
            $lawItemsBody.append($lawItemsTbl);
            $container.append($lawItemsBody);
            return $container;
        },
        //阿拉伯数字转汉字
        convertToChinese: function (num) {
            var N = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"];
            var str = num.toString();
            var len = num.toString().length;
            var C_Num = [];
            for (var i = 0; i < len; i++) {
                C_Num.push(N[str.charAt(i)]);
            }
            return C_Num.join('');
        },
        BindEvent: function () {
            //概要的点击事件
            $(".right .attribute .outline").toggle(function () {
                $(this).attr("class", "aclick tool_dir_common");
                $(".attribute .info").show(100);
            }, function () {
                $(this).attr("class", "outline tool_dir_common");
                $(".attribute .info").hide(100);
            });

            //关联条目的点击事件
            $("a[name='actItem']").click(function (docId) {
                $('#divLawItems').show();
            });
            $("#divLawItems").WinDrag(); //2015年11月23日,wangzhange 添加法律依据窗体可移动
        }
    };
    /**
    * 将内容盒子对象放置于jQuery的fn对象中
    */
    $.fn.ContentSummary = function (jsonData) {
        var plugin = $(this).data('divTool_Dir');
        if (typeof plugin == 'undefined' || null == plugin) {
            plugin = new Params(this, jsonData);
            plugin.Init();
            $(this).data('divTool_Dir', plugin);
        }
        return plugin;
    };
})(jQuery, window, document);


