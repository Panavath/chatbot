from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, date
from langchain_core.tools import Tool, ToolException

from app.database.models.minister_model import MinisterModel
from app.database.models.title_model import TitleModel
from app.database.models.sub_org_model import SubOrgModel
from app.database.models.content_model import ContentModel
from app.database.schemas.minister_schema import SubOrgSchema, MinisterSchema, ContentSchema
from app import logger

class MinisterTools:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def _get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="get_current_minister",
                func=self.get_current_minister,
                description="Get information about the current minister"
            ),
            Tool(
                name="get_minister_by_id",
                func=self.get_minister_by_id,
                description="Get minister information by ID. Args: minister_id (int)"
            ),
            Tool(
                name="get_all_ministers",
                func=self.get_all_ministers,
                description="Get all ministers with their titles"
            ),
            Tool(
                name="get_minister_by_year",
                func=self.get_minister_by_year,
                description="Get minister information for a specific year. Args: year (int)"
            ),
            Tool(
                name="get_sub_organizations",
                func=self.get_sub_organizations,
                description="Get all sub-organizations"
            ),
            Tool(
                name="get_content_by_page",
                func=self.get_content_by_page,
                description="Get content by page name. Args: page_name (str)"
            ),
            Tool(
                name="get_content_by_slug",
                func=self.get_content_by_slug,
                description="Get content by slug. Args: slug (str)"
            ),
            Tool(
                name="get_content_by_name",
                func=self.get_content_by_name,
                description="Get content by name. Args: name (str)"
            ),
            Tool(
                name="get_content_by_sub_org",
                func=self.get_content_by_sub_org,
                description="Get content by sub-organization Khmer name. Args: sub_org_kh_name (str)"
            ),
            Tool(
                name="search_content_by_keywords",
                func=self.search_content_by_keywords,
                description="Search content by keywords. Args: keywords (str)"
            ),
            Tool(
                name="search_content_by_slug",
                func=self.search_content_by_slug,
                description="Search content by slug. Args: slug (str)"
            ),
            Tool(
                name="search_ministers",
                func=self.search_ministers,
                description="Search ministers by name. Args: search_term (str)"
            )
        ]
    
    async def get_current_minister(self) -> Dict[str, Any]:
        """Get information about the current minister."""
        try:
            current_minister = (
                self.db.query(MinisterModel)
                .filter(MinisterModel.current == True)
                .first()
            )
            
            if not current_minister:
                raise ToolException("No current minister found")
            
            # Get title information separately to avoid relationship issues
            title = None
            if current_minister.title_id:
                title = self.db.query(TitleModel).filter(TitleModel.id == current_minister.title_id).first()
            
            return {
                "id": current_minister.id,
                "kh_name": current_minister.kh_name,
                "en_name": current_minister.en_name,
                "legislation": current_minister.legislation,
                "from_date": current_minister.from_date.isoformat() if current_minister.from_date else None,
                "to_date": current_minister.to_date.isoformat() if current_minister.to_date else None
            }
            
        except Exception as e:
            logger.error(f"Error getting current minister: {str(e)}")
            raise ToolException(str(e))
    
    async def get_minister_by_id(self, minister_id: int) -> Dict[str, Any]:
        """Get minister information by ID."""
        try:
            minister = (
                self.db.query(MinisterModel)
                .filter(MinisterModel.id == minister_id)
                .first()
            )
            
            if not minister:
                raise ToolException(f"Minister {minister_id} not found")
            
            # Get title information separately
            title = None
            if minister.title_id:
                title = self.db.query(TitleModel).filter(TitleModel.id == minister.title_id).first()
            
            return {
                "id": minister.id,
                "kh_name": minister.kh_name,
                "en_name": minister.en_name,
                "legislation": minister.legislation,
                "current": minister.current,
                "from_date": minister.from_date.isoformat() if minister.from_date else None,
                "to_date": minister.to_date.isoformat() if minister.to_date else None
            }
            
        except Exception as e:
            logger.error(f"Error getting minister by ID: {str(e)}")
            raise ToolException(str(e))
    
    async def get_all_ministers(self) -> List[Dict[str, Any]]:
        """Get all ministers with their titles."""
        try:
            ministers = (
                self.db.query(MinisterModel)
                .order_by(desc(MinisterModel.created_at))
                .all()
            )
            
            result = []
            for minister in ministers:
                result.append({
                    "id": minister.id,
                    "kh_name": minister.kh_name,
                    "en_name": minister.en_name,
                    "current": minister.current,
                    "legislation": minister.legislation,
                    "from_date": minister.from_date.isoformat() if minister.from_date else None,
                    "to_date": minister.to_date.isoformat() if minister.to_date else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting all ministers: {str(e)}")
            raise ToolException(str(e))
    
    async def get_minister_by_year(self, year: int) -> Dict[str, Any]:
        """Get minister information for a specific year."""
        try:
            from datetime import date
            
            # Create date objects for the year
            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)
            
            minister = (
                self.db.query(MinisterModel)
                .filter(
                    and_(
                        MinisterModel.from_date <= year_end,
                        MinisterModel.to_date >= year_start
                    )
                )
                .first()
            )
            
            if not minister:
                raise ToolException(f"No minister found for the year {year}")
            
            return {
                "id": minister.id,
                "kh_name": minister.kh_name,
                "en_name": minister.en_name,
                "legislation": minister.legislation,
                "current": minister.current,
                "from_date": minister.from_date.isoformat() if minister.from_date else None,
                "to_date": minister.to_date.isoformat() if minister.to_date else None,
                "year": year
            }
            
        except Exception as e:
            logger.error(f"Error getting minister by year: {str(e)}")
            raise ToolException(str(e))
    
    async def get_sub_organizations(self) -> List[Dict[str, Any]]:
        """Get all sub-organizations."""
        try:
            sub_orgs = (
                self.db.query(SubOrgModel)
                .order_by(SubOrgModel.kh_name)
                .all()
            )
            
            logger.info(f"Found {len(sub_orgs)} sub-organizations in database")
            
            # Convert to schema for validation
            result = []
            for org in sub_orgs:
                org_data = {
                    "id": org.id,
                    "kh_name": org.kh_name,
                    "en_name": org.en_name
                }
                # Validate with schema
                validated_org = SubOrgSchema(**org_data)
                result.append(validated_org.model_dump())
            
            logger.info(f"Returning {len(result)} validated sub-organizations")
            return result
            
        except Exception as e:
            logger.error(f"Error getting sub-organizations: {str(e)}")
            raise ToolException(str(e))
    
    async def get_content_by_page(self, page_name: str) -> Dict[str, Any]:
        """Get content by page name."""
        try:
            content = (
                self.db.query(ContentModel)
                .filter(ContentModel.page == page_name)
                .first()
            )
            
            if not content:
                raise ToolException(f"Content for page '{page_name}' not found")
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name
            }
            
        except Exception as e:
            logger.error(f"Error getting content by page: {str(e)}")
            raise ToolException(str(e))
    
    async def get_content_by_slug(self, slug: str) -> Dict[str, Any]:
        """Get content by slug."""
        try:
            content = (
                self.db.query(ContentModel)
                .filter(ContentModel.slug == slug)
                .first()
            )
            
            if not content:
                raise ToolException(f"Content for slug '{slug}' not found")
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name
            }
            
        except Exception as e:
            logger.error(f"Error getting content by slug: {str(e)}")
            raise ToolException(str(e))
    
    async def get_content_by_name(self, name: str) -> Dict[str, Any]:
        """Get content by name."""
        try:
            content = (
                self.db.query(ContentModel)
                .filter(ContentModel.name == name)
                .first()
            )
            
            if not content:
                raise ToolException(f"Content for name '{name}' not found")
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name
            }
            
        except Exception as e:
            logger.error(f"Error getting content by name: {str(e)}")
            raise ToolException(str(e))
    
    async def get_content_by_sub_org(self, sub_org_kh_name: str) -> Dict[str, Any]:
        """Get content by sub-organization Khmer name."""
        try:
            content = (
                self.db.query(ContentModel)
                .filter(ContentModel.name == sub_org_kh_name)
                .first()
            )
            
            if not content:
                raise ToolException(f"Content for sub-organization '{sub_org_kh_name}' not found")
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name
            }
            
        except Exception as e:
            logger.error(f"Error getting content by sub-org: {str(e)}")
            raise ToolException(str(e))
    
    async def get_content_by_slug_and_page(self, slug: str, page: str = "home") -> Dict[str, Any]:
        """Get content by slug and page (useful for sub-organizations)."""
        try:
            content = (
                self.db.query(ContentModel)
                .filter(
                    ContentModel.slug == slug,
                    ContentModel.page == page
                )
                .first()
            )
            
            if not content:
                raise ToolException(f"Content for slug '{slug}' and page '{page}' not found")
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name
            }
            
        except Exception as e:
            logger.error(f"Error getting content by slug and page: {str(e)}")
            raise ToolException(str(e))
    
    async def search_content_by_keywords(self, keywords: str) -> Dict[str, Any]:
        """Search content by keywords in title or content."""
        try:
            from sqlalchemy import or_
            
            logger.info(f"Searching for keywords: '{keywords}'")
            
            # Search in both English and Khmer content and titles
            contents = (
                self.db.query(ContentModel)
                .filter(
                    or_(
                        ContentModel.en_title.ilike(f"%{keywords}%"),
                        ContentModel.kh_title.ilike(f"%{keywords}%"),
                        ContentModel.en_content.ilike(f"%{keywords}%"),
                        ContentModel.kh_content.ilike(f"%{keywords}%"),
                        ContentModel.name.ilike(f"%{keywords}%"),
                        ContentModel.page.ilike(f"%{keywords}%"),
                        ContentModel.slug.ilike(f"%{keywords}%")
                    )
                )
                .all()
            )
            
            logger.info(f"Found {len(contents)} content items for keywords '{keywords}'")
            
            if not contents:
                raise ToolException(f"No content found matching keywords '{keywords}'")
            
            # Prioritize content based on relevance
            # 1. Exact matches in title
            # 2. Partial matches in title
            # 3. Content matches
            # 4. Page/slug matches
            
            prioritized_contents = []
            for content in contents:
                score = 0
                
                # Exact title matches get highest priority
                if keywords.lower() in content.en_title.lower() or keywords.lower() in content.kh_title.lower():
                    score += 100
                
                # Partial title matches
                if any(word in content.en_title.lower() for word in keywords.lower().split()) or \
                   any(word in content.kh_title.lower() for word in keywords.lower().split()):
                    score += 50
                
                # Content matches
                if keywords.lower() in content.en_content.lower() or keywords.lower() in content.kh_content.lower():
                    score += 25
                
                # Name/slug matches
                if keywords.lower() in content.name.lower() or keywords.lower() in content.slug.lower():
                    score += 10
                
                prioritized_contents.append((content, score))
            
            # Sort by score and return the best match
            prioritized_contents.sort(key=lambda x: x[1], reverse=True)
            content = prioritized_contents[0][0]
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name,
                "search_keywords": keywords,
                "relevance_score": prioritized_contents[0][1]
            }
            
        except Exception as e:
            logger.error(f"Error searching content by keywords: {str(e)}")
            raise ToolException(str(e))
    
    async def search_content_by_slug(self, slug: str) -> Dict[str, Any]:
        """Search content by slug specifically."""
        try:
            # First try exact slug match
            content = (
                self.db.query(ContentModel)
                .filter(ContentModel.slug == slug)
                .first()
            )
            
            if not content:
                # Try partial slug match
                content = (
                    self.db.query(ContentModel)
                    .filter(ContentModel.slug.ilike(f"%{slug}%"))
                    .first()
                )
            
            if not content:
                raise ToolException(f"No content found for slug '{slug}'")
            
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name,
                "search_keywords": slug
            }
            
        except Exception as e:
            logger.error(f"Error searching content by slug: {str(e)}")
            raise ToolException(str(e))
    
    async def search_content_by_sub_org_name(self, sub_org_name: str) -> Dict[str, Any]:
        """Search content by sub-organization name more specifically."""
        try:
            from sqlalchemy import or_
            
            # Try exact matches first
            contents = (
                self.db.query(ContentModel)
                .filter(
                    or_(
                        ContentModel.name == sub_org_name,
                        ContentModel.kh_title == sub_org_name,
                        ContentModel.en_title == sub_org_name
                    )
                )
                .all()
            )
            
            if not contents:
                # Try partial matches
                contents = (
                    self.db.query(ContentModel)
                    .filter(
                        or_(
                            ContentModel.name.ilike(f"%{sub_org_name}%"),
                            ContentModel.kh_title.ilike(f"%{sub_org_name}%"),
                            ContentModel.en_title.ilike(f"%{sub_org_name}%"),
                            ContentModel.en_content.ilike(f"%{sub_org_name}%"),
                            ContentModel.kh_content.ilike(f"%{sub_org_name}%")
                        )
                    )
                    .all()
                )
            
            if not contents:
                raise ToolException(f"No content found for sub-organization '{sub_org_name}'")
            
            # Return the first matching content
            content = contents[0]
            return {
                "id": content.id,
                "page": content.page,
                "slug": content.slug,
                "name": content.name,
                "kh_title": content.kh_title,
                "en_title": content.en_title,
                "image": content.image,
                "kh_content": content.kh_content,
                "en_content": content.en_content,
                "editor_name": content.editor_name,
                "search_keywords": sub_org_name
            }
            
        except Exception as e:
            logger.error(f"Error searching content by sub-org name: {str(e)}")
            raise ToolException(str(e))
    
    async def search_ministers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search ministers by name."""
        try:
            ministers = (
                self.db.query(MinisterModel)
                .filter(
                    or_(
                        MinisterModel.kh_name.ilike(f"%{search_term}%"),
                        MinisterModel.en_name.ilike(f"%{search_term}%")
                    )
                )
                .order_by(desc(MinisterModel.created_at))
                .all()
            )
            
            result = []
            for minister in ministers:
                result.append({
                    "id": minister.id,
                    "kh_name": minister.kh_name,
                    "en_name": minister.en_name,
                    "current": minister.current,
                    "legislation": minister.legislation,
                    "from_date": minister.from_date.isoformat() if minister.from_date else None,
                    "to_date": minister.to_date.isoformat() if minister.to_date else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching ministers: {str(e)}")
            raise ToolException(str(e)) 