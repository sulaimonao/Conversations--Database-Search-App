SELECT c.conversation_id, c.title, c.create_time, c.update_time, m.message_id, m.content
FROM Conversations c
LEFT JOIN Messages m ON c.conversation_id = m.conversation_id
LIMIT 10;