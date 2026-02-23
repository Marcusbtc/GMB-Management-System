from datetime import datetime, timedelta

def calculate_days_since(date_str):
    """Calculates days since a given date string (ISO format or YYYY-MM-DD)."""
    if not date_str:
        return None
    try:
        # Handle various date formats if needed, assuming ISO or YYYY-MM-DD
        if 'T' in date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Simple YYYY-MM-DD
            parts = date_str.split('-')
            if len(parts) == 3:
                 date_obj = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
            else:
                return None
        
        delta = datetime.now(date_obj.tzinfo) - date_obj
        return delta.days
    except Exception:
        return None

def analyze_profile_health(location_details, reviews, posts, media_items, questions):
    """
    Analyzes the health of a Google Business Profile based on detailed metrics.
    Returns a list of check results.
    Each result: {
        'title': str,
        'description': str,
        'status': 'Weak' | 'Reasonable' | 'Good',
        'score': int (0-100),
        'value': str (optional display value),
        'recommendation': str
    }
    """
    results = []
    
    # Helper to add result
    def add_result(title, description, status, score, value=None, recommendation=""):
        results.append({
            'title': title,
            'description': description,
            'status': status,
            'score': score,
            'value': value,
            'recommendation': recommendation
        })

    # 1. Foundation Date
    opening_date = location_details.get('openInfo', {}).get('openingDate')
    if opening_date:
        add_result(
            "Data de Fundação",
            "Informe aos seus clientes quando o seu negócio foi fundado.",
            "Good", 100,
            value=f"{opening_date.get('day')}/{opening_date.get('month')}/{opening_date.get('year')}",
            recommendation="Data de fundação definida."
        )
    else:
        add_result(
            "Data de Fundação",
            "Informe aos seus clientes quando o seu negócio foi fundado.",
            "Weak", 0,
            recommendation="O negócio ainda não possui data de fundação adicionada."
        )

    # 2. Unanswered Reviews
    total_reviews = len(reviews)
    unanswered_count = sum(1 for r in reviews if 'reviewReply' not in r)
    if total_reviews > 0:
        response_rate = ((total_reviews - unanswered_count) / total_reviews) * 100
        if response_rate >= 90:
            status, score = "Good", 100
        elif response_rate >= 50:
            status, score = "Reasonable", 50
        else:
            status, score = "Weak", 0
            
        add_result(
            "Avaliações - Avaliações Sem Resposta",
            "Os seus clientes investiram tempo escrevendo uma avaliação. Responder mostra o quanto você se importa.",
            status, score,
            value=f"{unanswered_count} sem resposta",
            recommendation=f"Ainda não existem avaliações em quantidades suficientes respondidas. Total: {total_reviews}. Sem resposta: {unanswered_count}."
        )
    else:
         add_result(
            "Avaliações - Avaliações Sem Resposta",
            "Os seus clientes investiram tempo escrevendo uma avaliação.",
            "Reasonable", 50,
            recommendation="Não há avaliações para responder."
        )

    # 3. Media - Videos
    video_count = sum(1 for m in media_items if m.get('mediaFormat') == 'VIDEO')
    if video_count >= 3:
        add_result("Mídia - Vídeos", "Vídeos atraem e fidelizam clientes.", "Good", 100, value=str(video_count))
    elif video_count > 0:
        add_result("Mídia - Vídeos", "Vídeos atraem e fidelizam clientes.", "Reasonable", 50, value=str(video_count))
    else:
        add_result("Mídia - Vídeos", "Vídeos atraem e fidelizam clientes.", "Weak", 0, recommendation="Não existem vídeos para o negócio. Recomendado: 3.")

    # 4. Last Media by Owner
    # Filter media by owner (association is usually 'SOURCE_OWNER' or similar, but API might just give all)
    # Assuming all fetched media is relevant.
    if media_items:
        # Sort by createTime
        sorted_media = sorted(media_items, key=lambda x: x.get('createTime', ''), reverse=True)
        last_media_date = sorted_media[0].get('createTime')
        days_since_media = calculate_days_since(last_media_date)
        
        if days_since_media is not None:
            if days_since_media <= 30:
                status, score = "Good", 100
            elif days_since_media <= 60:
                status, score = "Reasonable", 50
            else:
                status, score = "Weak", 0
            
            add_result(
                "Data da Última Mídia pelo Proprietário",
                "Publicar periodicamente fotos ou vídeos demonstra que o seu perfil está ativo.",
                status, score,
                value=f"{days_since_media} dias",
                recommendation=f"Dias desde a última mídia: {days_since_media}. Máximo recomendado: 60 dias."
            )
    else:
        add_result("Data da Última Mídia pelo Proprietário", "Publicar periodicamente fotos ou vídeos.", "Weak", 0, recommendation="Nenhuma mídia encontrada.")

    # 5. Last Post
    if posts:
        # Sort by createTime (posts usually have createTime or updateTime)
        # Assuming posts list is already sorted or we sort it
        # API posts usually have 'createTime'
        # Let's assume the list from API is recent first or sort it
        # Note: API might return 'searchUrl' etc. Need to check structure.
        # Assuming standard structure.
        # Safely get date
        valid_posts = [p for p in posts if p.get('createTime')]
        if valid_posts:
            sorted_posts = sorted(valid_posts, key=lambda x: x.get('createTime'), reverse=True)
            last_post_date = sorted_posts[0].get('createTime')
            days_since_post = calculate_days_since(last_post_date)
            
            if days_since_post is not None:
                if days_since_post <= 7:
                    status, score = "Good", 100
                elif days_since_post <= 30:
                    status, score = "Reasonable", 50
                else:
                    status, score = "Weak", 0
                
                add_result(
                    "Data da Última Postagem",
                    "Criar e compartilhar novidades demonstra que o seu negócio é ativo.",
                    status, score,
                    value=f"{days_since_post} dias",
                    recommendation=f"Dias desde a última postagem: {days_since_post}. Máximo recomendado: 30 dias."
                )
        else:
             add_result("Data da Última Postagem", "Criar e compartilhar novidades.", "Weak", 0, recommendation="Nenhuma postagem válida encontrada.")
    else:
        add_result("Data da Última Postagem", "Criar e compartilhar novidades.", "Weak", 0, recommendation="Nenhuma postagem encontrada.")

    # 6. Review Trends (Simplified logic: Compare avg of last 5 vs total avg)
    if total_reviews >= 5:
        # Assuming reviews are sorted recent first
        recent_reviews = reviews[:5]
        
        def get_rating(r):
            # rating can be 'STAR_RATING_UNSPECIFIED' or string 'FIVE' etc in some API versions
            # But usually it's a string "FIVE" or int.
            # Let's handle string enum if needed.
            rating = r.get('starRating', '0')
            if isinstance(rating, int): return rating
            mapping = {'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4, 'FIVE': 5}
            return mapping.get(rating, 0)

        recent_avg = sum(get_rating(r) for r in recent_reviews) / 5
        # Total avg is usually in location_details but let's calc from fetched reviews for consistency
        total_avg = sum(get_rating(r) for r in reviews) / total_reviews
        
        if recent_avg >= total_avg:
            status, score = "Good", 100
            rec = "A média de avaliações recentes está estável ou subindo."
        else:
            status, score = "Weak", 0
            rec = "A média de avaliações recentes está caindo e pode indicar um problema."
            
        add_result("Avaliações - Comparativo", "Analisa o histórico de avaliações recentes.", status, score, recommendation=rec)
    else:
        add_result("Avaliações - Comparativo", "Analisa o histórico de avaliações recentes.", "Reasonable", 50, recommendation="Dados insuficientes para tendência.")

    # 7. Special Hours
    special_hours = location_details.get('specialHours')
    if special_hours:
        add_result("Horário Especial", "Importante definir horário especial para feriados.", "Good", 100, recommendation="Horário especial definido.")
    else:
        add_result("Horário Especial", "Importante definir horário especial para feriados.", "Weak", 0, recommendation="Ainda não existe horário especial definido.")

    # 8. Q&A
    total_questions = len(questions)
    if total_questions >= 1:
        add_result("Perguntas e Respostas", "Responda a perguntas diretas de clientes.", "Good", 100, value=str(total_questions))
    else:
        add_result("Perguntas e Respostas", "Responda a perguntas diretas de clientes.", "Weak", 50, recommendation="Ainda não existem perguntas. Recomendado: 1.")

    # 9. Business Name
    name = location_details.get('title', '')
    if len(name) <= 98:
        add_result("Nome do Negócio", "O nome deve refletir o nome real do negócio.", "Good", 100, value=f"{len(name)} chars")
    else:
        add_result("Nome do Negócio", "O nome deve refletir o nome real do negócio.", "Weak", 0, recommendation="Nome muito longo.")

    # 10. Phone Number
    if location_details.get('phoneNumbers'):
        add_result("Número de Telefone", "Informação chave para o negócio.", "Good", 100, recommendation="Telefone definido.")
    else:
        add_result("Número de Telefone", "Informação chave para o negócio.", "Weak", 0, recommendation="Adicione um telefone.")

    # 11. Website
    if location_details.get('websiteUri'):
        add_result("Website", "Dá credibilidade e contato.", "Good", 100, recommendation="Website definido.")
    else:
        add_result("Website", "Dá credibilidade e contato.", "Weak", 0, recommendation="Adicione um website.")

    # 12. Description
    description = location_details.get('profile', {}).get('description', '')
    # Sometimes description is directly on location object in some API versions?
    # Let's check keys.
    if not description:
        # Try to find it elsewhere or assume missing
        pass
        
    if len(description) >= 50:
        add_result("Descrição da Empresa", "Conte a sua história.", "Good", 100, value=f"{len(description)} chars")
    else:
        add_result("Descrição da Empresa", "Conte a sua história.", "Weak", 0, recommendation="Descrição curta ou ausente. Mínimo 50 caracteres.")

    return results
