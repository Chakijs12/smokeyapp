<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:exsl="http://exslt.org/common" extension-element-prefixes="exsl">

	<xsl:output method="text" encoding="UTF-8" indent="yes" />

	<xsl:variable name="apos">
		<xsl:text>'</xsl:text>
	</xsl:variable>
	<xsl:variable name="element_separator" select="'+'" />
	<xsl:variable name="subelement_separator" select="':'" />
	<xsl:variable name="segment_terminator" select="$apos" />
	<xsl:variable name="eol" select="'&#10;'" />

	<!-- Root template -->
	<xsl:template match="/">
		<!-- Now transform 'edifact-segment' elements to EDIFACT segments -->
		<xsl:apply-templates select="interchange/document" />
	</xsl:template>

	<xsl:template match="document">
		<xsl:apply-templates select="segment" />
	</xsl:template>

	<!-- Template to output one segment -->
	<!-- (usually, segment ends with a single quote and optional EOL) -->
	<xsl:template match="segment">
		<xsl:value-of select="@tag" />
		<xsl:choose>
			<xsl:when test="@tag = 'UNA'">
				<xsl:value-of select="$subelement_separator" />
				<xsl:value-of select="$element_separator" />
				<xsl:text>.? </xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="str">
					<xsl:apply-templates select="element" />
				</xsl:variable>
				<xsl:call-template name="remove_trailing_separators">
					<xsl:with-param name="str" select="$str" />
					<xsl:with-param name="separator" select="$element_separator" />
				</xsl:call-template>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:value-of select="$segment_terminator" />
		<xsl:value-of select="$eol" />
	</xsl:template>

	<xsl:template match="element">
		<xsl:value-of select="$element_separator" />
		<xsl:choose>
			<xsl:when test="subelement">
				<xsl:variable name="str">
					<xsl:apply-templates select="subelement" />
				</xsl:variable>
				<xsl:call-template name="remove_trailing_separators">
					<xsl:with-param name="str" select="$str" />
					<xsl:with-param name="separator" select="$subelement_separator" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="normalize-space(.)" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="subelement">
		<xsl:if test="position() &gt; 1">
			<xsl:value-of select="$subelement_separator" />
		</xsl:if>
		<xsl:value-of select="normalize-space(.)" />
	</xsl:template>

	<xsl:template name="remove_trailing_separators">
		<xsl:param name="str" />
		<xsl:param name="separator" />
		<xsl:variable name="str_len" select="string-length($str)" />
		<xsl:choose>
			<xsl:when test="($str_len > 0) and (substring($str, $str_len, 1) = $separator)">
				<xsl:call-template name="remove_trailing_separators">
					<xsl:with-param name="str" select="substring($str, 1, $str_len - 1)" />
					<xsl:with-param name="separator" select="$separator" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$str" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="string_to_parts">
		<xsl:param name="str" />
		<xsl:param name="part_length" />
		<xsl:param name="max_parts" />
		<xsl:variable name="str_length" select="string-length($str)" />
		<xsl:if
			test="($part_length &gt; 0) and ($max_parts &gt; 0) and ($str_length &gt; 0)">
			<subelement>
				<xsl:value-of select="substring($str, 1, $part_length)" />
			</subelement>
			<xsl:call-template name="string_to_parts">
				<xsl:with-param name="str" select="substring($str, $part_length + 1)" />
				<xsl:with-param name="part_length" select="$part_length" />
				<xsl:with-param name="max_parts" select="$max_parts - 1" />
			</xsl:call-template>
		</xsl:if>
	</xsl:template>

	<xsl:template name="escaped_string_to_parts">
		<xsl:param name="str" />
		<xsl:param name="part_length" />
		<xsl:param name="max_parts" />
		<xsl:variable name="escaped_str">
			<xsl:call-template name="escape_string">
				<xsl:with-param name="text" select="$str" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:call-template name="string_to_parts">
			<xsl:with-param name="str" select="$escaped_str" />
			<xsl:with-param name="part_length" select="$part_length" />
			<xsl:with-param name="max_parts" select="$max_parts - 1" />
		</xsl:call-template>
	</xsl:template>

	<xsl:template name="replace_string">
		<xsl:param name="text" />
		<xsl:param name="replace" />
		<xsl:param name="with" />
		<xsl:choose>
			<xsl:when test="contains($text,$replace)">
				<xsl:value-of select="substring-before($text, $replace)" />
				<xsl:value-of select="$with" />
				<xsl:call-template name="replace_string">
					<xsl:with-param name="text" select="substring-after($text, $replace)" />
					<xsl:with-param name="replace" select="$replace" />
					<xsl:with-param name="with" select="$with" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$text" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="escape_string">
		<xsl:param name="text" />
		<xsl:variable name="text1">
			<xsl:call-template name="replace_string">
				<xsl:with-param name="text" select="$text" />
				<xsl:with-param name="replace" select="'?'" />
				<xsl:with-param name="with" select="'??'" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:variable name="text2">
			<xsl:call-template name="replace_string">
				<xsl:with-param name="text" select="$text1" />
				<xsl:with-param name="replace" select="'+'" />
				<xsl:with-param name="with" select="'?+'" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:variable name="text3">
			<xsl:call-template name="replace_string">
				<xsl:with-param name="text" select="$text2" />
				<xsl:with-param name="replace" select="':'" />
				<xsl:with-param name="with" select="'?:'" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:call-template name="replace_string">
			<xsl:with-param name="text" select="$text3" />
			<xsl:with-param name="replace" select="$apos" />
			<xsl:with-param name="with" select="concat('?', $apos)" />
		</xsl:call-template>
	</xsl:template>

</xsl:stylesheet>
<!-- Stylus Studio meta-information - (c) 2004-2009. Progress Software Corporation. All rights reserved.

<metaInformation>
	<scenarios>
		<scenario default="yes" name="original_standard_INVOICE_DS041624 (7).xml" userelativepaths="yes" externalpreview="no" url="..\..\Downloads\standard_INVOICE_DS041624 (3).xml" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes"
		          profilemode="0" profiledepth="" profilelength="" urlprofilexml="" commandline="" additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext=""
		          validateoutput="no" validator="internal" customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
	</scenarios>
	<MapperMetaTag>
		<MapperInfo srcSchemaPathIsRelative="yes" srcSchemaInterpretAsXML="no" destSchemaPath="" destSchemaRoot="" destSchemaPathIsRelative="yes" destSchemaInterpretAsXML="no"/>
		<MapperBlockPosition></MapperBlockPosition>
		<TemplateContext></TemplateContext>
		<MapperFilter side="source"></MapperFilter>
	</MapperMetaTag>
</metaInformation>
-->