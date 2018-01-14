from . import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

# ___________ 方法2. WebhookHandler______________
''' 
WebhookHandler 是針對每一種不同的訊息型態註冊一個處理器
只要收到這樣的訊息，就會丟給對應的處理器，如果確定每一類訊息
，在任何情況下都會有相似的處理方式，就很適合這樣的設計
'''
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text) )

@handler.default()
def default(event):
    '''
    如果收到其他訊息(e.g. 貼圖, 照片)或訊息以外的事件
    使用default來回傳"Currently Not Support None Text Message"的文字訊息
    '''
    print(event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Currently Not Support None Text Message')
    )

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
    
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

"""
# ___________ 方法1. WebhookParser ______________
# Define Receiver
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    '''
    處理訊息之前，必須先確認這個request是不是真的是從Line Server傳來的
    ，要確認這件事，需要:
    1. request 的 body
    2. request header 中的 X-Line-Signature
    '''
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        
        '''
        取得 body 跟 signature 後 Line Bot API會在處理訊息的同時，
        確認這個訊息是否來自Line，而處理 Line 傳過來給我們的訊息，有
        兩種不同的做法:
        方法1. WebhookParser
        WebhookParser 會 parse 這個訊息的所有欄位讓我們針對各種不同
        型別的訊息做個別的處理
        ex:
        UserID, Event Type, Message Content, and etc.
        '''
        try:
            events = parser.parse(body, signature)
            '''
            先判斷這個事件是不是訊息事件，而這個訊息是不是文字訊息
            最後的reply_message函式，讓我們傳訊息給Line Server
            第一個參數是要回傳要用的reply_token，可以從事件中取得 
            （event.reply_token）使用這個 reply_token 做回覆，
            是不用收費的，不過同一個 reply_token 只能使用一次，
            而且在一定的時間內就會失效
            第二個參數是這次要回傳的訊息，所有能回傳的訊息:
            https://github.com/line/line-bot-sdk-python#send-message-object
            也可以傳一個都是訊息的 list 或 tuple，不過一次最多只能
            傳5個只要超過就會有 LineBotApiError
            '''
            for event in events:
                if (isinstance(event, MessageEvent) and 
                    isinstance(event.message, TextMessage)):
                    line_bot_api.reply_message (
                        event.reply_token,
                        TextSendMessage(text=event.message.text)
                    )
            '''
            如果 request 不是從 Line Server 來的，就會丟出
            InvalidSignatureError，其他使用錯誤，或 Line 
            Server 的問題都會是丟出 LineBotApiError
            '''
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
"""

