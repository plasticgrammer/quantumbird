from typing import Dict, Any
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def format_insights_response(claude_response: str) -> Dict[str, Any]:
    """Claudeのレスポンスを整形する"""
    try:
        result = json.loads(claude_response)
        if not isinstance(result, dict) or 'summary' not in result or 'insights' not in result:
            return {
                'summary': 'サマリーの生成に失敗しました。',
                'insights': {
                    'positive': [],
                    'negative': []
                }
            }
            
        insights = result.get('insights', {})
        if isinstance(insights, dict):
            if isinstance(insights.get('positive'), list):
                insights['positive'] = sorted(
                    insights['positive'],
                    key=lambda x: float(x.get('score', 0)),
                    reverse=True
                )
            if isinstance(insights.get('negative'), list):
                insights['negative'] = sorted(
                    insights['negative'],
                    key=lambda x: float(x.get('score', 0)),
                    reverse=True
                )
                
        return {
            'summary': result.get('summary', ''),
            'insights': insights
        }
        
    except json.JSONDecodeError:
        return {
            'summary': 'サマリーの生成に失敗しました。',
            'insights': {
                'positive': [],
                'negative': []
            }
        }
