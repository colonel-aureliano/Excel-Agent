function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Sheets AI Agent')
    .addItem('Open Chat', 'showChatSidebar')
    .addToUi();
}

function onInstall(e) {
  onOpen(e);
}

function showChatSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('ChatSidebar')
    .setTitle('Sheets AI Agent')
    .setWidth(350); // Adjust width as needed
  SpreadsheetApp.getUi().showSidebar(html);
}
