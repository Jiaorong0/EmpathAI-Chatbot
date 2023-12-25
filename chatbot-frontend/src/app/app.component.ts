import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface ChatMessage {
  text: string;
  sender: string;
  sentiment_score?: number;
  sentiment?: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'chatbot-frontend';
  userMessage = '';
  conversation: ChatMessage[] = [];
  userId = 'user123';

  constructor(private http: HttpClient) {}

  sendMessage() {
    const message = this.userMessage;

    this.conversation.push({
      text: message,
      sender: 'user',
    });
    this.userMessage = '';

    this.http.post('http://localhost:5000/chat', { userId: this.userId, prompt: this.conversation })
      .subscribe((response: any) => {

        this.conversation[this.conversation.length - 1].sentiment_score = response.sentiment_score;
        this.conversation[this.conversation.length - 1].sentiment = response.sentiment
        this.conversation.push({
          text: response.response,
          sender: 'assistant' });
      });





  }
}
