ckan.module('nsw_likes', function($, _) {
    "use strict";
    return {
        options : {
            entity_id: null,
            entity_name: null,
            entity_type: null
        },
        initialize: function() {
            $.proxyAll(this, /_on/);
            jQuery(this.el).on('click', this._onClick);
        },
        _onClick: function(event) {
            var client = this.sandbox.client;
            var options = this.options;
            if(options.entity_id && options.entity_name && options.entity_type){
                var opts_obj = {
                    entity_id : options.entity_id,
                    entity_name : options.entity_name,
                    entity_type : options.entity_type,
                };
                client.call('POST', 'handle_likes', opts_obj, this._onResponse);
            } else {
                console.log("Missing some property.");
            };
        },
        _onResponse: function(json) {
            var result = json.result;
            var el = $(this.el);
            if (result.success) {
                if(result.liked_flag) {
                    el.removeClass('like-button').addClass('unlike-button').attr("title", "You like it").html('<i class="fa fa-thumbs-up" aria-hidden="true"></i>');
                } else {
                    el.removeClass('unlike-button').addClass('like-button').attr("title", "Like").html('<i class="fa fa-thumbs-o-up" aria-hidden="true"></i>');
                };
                $(this.el).parent().find('#likes-count').text(result.count);
            };
        },
    };
});
